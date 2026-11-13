import logging
import uuid
from typing import Any, Dict, Optional
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server.config import ALLOWED_ORIGINS, MAPS_DIR
from server.science import run_analysis
from server.availability import query_availability
from server.caching import compute_cache_key, get_cached_result, save_result_to_cache
from server.jobs import (
    load_jobs_from_disk,
    create_job_record,
    get_job_record,
    update_job_step,
    complete_job,
    fail_job,
)
from server.validation import parse_and_validate_area

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="NISAR Change Explorer API", version="0.2.0")

# Load existing jobs from disk on boot
load_jobs_from_disk()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standardized Error Handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # If detail is already a structured dict with code and message, preserve it
    if isinstance(exc.detail, dict) and "code" in exc.detail and "message" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
    code = "UPSTREAM_FAILURE" if exc.status_code >= 500 else "INVALID_REQUEST"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": str(exc.detail)}},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "UPSTREAM_FAILURE", "message": f"Server encountered an error: {str(exc)}. Please retry shortly."}},
    )

# Static route serving map overlay images from CACHE_DIR/maps
MAPS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/results", StaticFiles(directory=str(MAPS_DIR)), name="results_static")

# Request Schemas
class AvailabilityRequest(BaseModel):
    area: Optional[Any] = None
    start_date: Optional[str] = "2024-10-01"
    end_date: Optional[str] = "2024-10-15"

class AnalysisRequest(BaseModel):
    area: Optional[Any] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    dates: Optional[Dict[str, str]] = None
    question: Optional[str] = "flood_wetland"
    analysis_type: Optional[str] = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/availability")
def availability(req: AvailabilityRequest):
    """
    Check what NISAR passes exist for the area.
    Catalogue query only; returns mode 'live' or 'sample'.
    """
    if req.area is None:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_REQUEST", "message": "Field 'area' is required. Please provide a bounding box {west, south, east, north}."}
        )
    validated_area = parse_and_validate_area(req.area)
    start_date = req.start_date or "2024-10-01"
    end_date = req.end_date or "2024-10-15"

    return query_availability(validated_area, start_date, end_date)

def _execute_analysis_background(
    job_id: str,
    area: Dict[str, float],
    start_date: str,
    end_date: str,
    question: str,
    cache_key: str
) -> None:
    """Worker task executed in background thread pool."""
    try:
        def on_progress(step_message: str):
            update_job_step(job_id, step_message)

        # Check availability first to enforce INSUFFICIENT_DATA check if fewer than 2 passes exist
        avail = query_availability(area, start_date, end_date)
        passes = avail.get("passes", [])
        if len(passes) < 2:
            fail_job(
                job_id,
                code="INSUFFICIENT_DATA",
                message=f"Only {len(passes)} usable pass found for this timeframe. At least 2 passes are required for change detection. Please expand your date range."
            )
            return

        result = run_analysis(
            area=area,
            start_date=start_date,
            end_date=end_date,
            question=question,
            progress=on_progress
        )

        # Cache the completed result
        save_result_to_cache(cache_key, result)

        # Complete the job
        complete_job(job_id, result)
    except Exception as exc:
        logger.exception("Job %s execution failed: %s", job_id, exc)
        fail_job(
            job_id,
            code="UPSTREAM_FAILURE",
            message=f"Analysis pipeline error: {str(exc)}. Please try again."
        )

@app.post("/analyze")
def analyze(req: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Dispatches change analysis in background. Returns job_id immediately.
    If exact query is cached, serves saved result instantly.
    """
    if req.area is None:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_REQUEST", "message": "Field 'area' is required. Please provide a bounding box {west, south, east, north}."}
        )
    validated_area = parse_and_validate_area(req.area)

    # Extract dates from dates dict or top-level fields
    start_date = req.start_date
    end_date = req.end_date
    if req.dates:
        start_date = start_date or req.dates.get("pre_event") or req.dates.get("start")
        end_date = end_date or req.dates.get("post_event") or req.dates.get("end")

    if not start_date or not end_date:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_REQUEST", "message": "Both 'start_date' and 'end_date' (or dates.pre_event and dates.post_event) are required."}
        )

    question = req.question or req.analysis_type or "flood_wetland"
    cache_key = compute_cache_key(validated_area, start_date, end_date, question)

    # Check cache hit
    cached = get_cached_result(cache_key)
    job_id = str(uuid.uuid4())
    create_job_record(job_id)

    if cached:
        logger.info("Cache hit for key %s, returning saved result immediately", cache_key)
        complete_job(job_id, cached)
        return {"job_id": job_id, "cached": True}

    # Dispatch background execution
    background_tasks.add_task(
        _execute_analysis_background,
        job_id=job_id,
        area=validated_area,
        start_date=start_date,
        end_date=end_date,
        question=question,
        cache_key=cache_key
    )
    return {"job_id": job_id, "cached": False}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = get_job_record(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail={"code": "404", "message": f"Job '{job_id}' not found. Please verify the job identifier."}
        )
    resp = {
        "job_id": job_id,
        "status": job["status"],
        "step": job["step"]
    }
    if job["status"] == "failed" and job.get("error"):
        resp["error"] = job["error"]
    return resp

@app.get("/results/{job_id}")
def get_result(job_id: str):
    job = get_job_record(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail={"code": "404", "message": f"Result for job '{job_id}' not found."}
        )
    if job["status"] == "failed":
        err = job.get("error") or {"code": "UPSTREAM_FAILURE", "message": "Job failed during processing."}
        raise HTTPException(status_code=400, detail=err)

    if job["status"] != "complete" or not job.get("result"):
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_REQUEST", "message": f"Job is currently {job['status']} ('{job['step']}'). Result is not ready yet."}
        )

    return job["result"]
