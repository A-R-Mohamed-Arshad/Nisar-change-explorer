import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="NISAR Change Explorer API", version="0.1.0")

# Setup CORS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
if not origins:
    origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standardized Error Handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": str(exc.status_code), "message": str(exc.detail)}},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(exc)}},
    )

# Path to sample result file in data/sample/
BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_RESULT_PATH = BASE_DIR / "data" / "sample" / "sample-result.json"

def load_sample_result() -> Dict[str, Any]:
    if SAMPLE_RESULT_PATH.exists():
        with open(SAMPLE_RESULT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "_note": "Fallback sample result (file not found on disk)",
        "status": "complete",
        "mode": "sample",
        "area": None,
        "dates_used": {},
        "files_used": [],
        "result_map_url": "",
        "area_changed_by_category": {},
        "confidence": 0.0,
        "confidence_reason": "No sample file",
        "limits": "Sample placeholder",
        "source_type": "Sample"
    }

# In-memory jobs dictionary
# Schema: job_id -> {"status": "queued"|"running"|"complete"|"failed", "step": str, "result": dict}
# TODO: Real persistent storage or distributed cache (e.g. Redis) will be plugged in later.
jobs_db: Dict[str, Dict[str, Any]] = {}

class AvailabilityRequest(BaseModel):
    area: Optional[Dict[str, Any]] = None
    date_range: Optional[Dict[str, str]] = None

class AnalysisRequest(BaseModel):
    area: Optional[Dict[str, Any]] = None
    dates: Optional[Dict[str, str]] = None
    analysis_type: Optional[str] = "flood_wetland"

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/availability")
def availability(req: AvailabilityRequest):
    """
    Check what NISAR passes exist for the area.
    TODO: Plug in earthaccess and asf_search here to query CMR and ASF DAAC for real NISAR granules.
    """
    sample_passes = [
        {
            "granule_id": "NISAR_L2_PR_GCOV_001_005_A_123_20241001T000000_20241001T000030_M01_F_J_001.h5",
            "date": "2024-10-01",
            "orbit_direction": "Ascending",
            "quality_level": "nominal"
        },
        {
            "granule_id": "NISAR_L2_PR_GCOV_001_005_A_123_20241015T000000_20241015T000030_M01_F_J_001.h5",
            "date": "2024-10-15",
            "orbit_direction": "Ascending",
            "quality_level": "nominal"
        }
    ]
    return {
        "status": "complete",
        "mode": "sample",
        "passes": sample_passes
    }

@app.post("/analyze")
def analyze(req: AnalysisRequest):
    """
    Start change detection analysis.
    Returns a job_id immediately.
    TODO: Real science function (raster processing, backscatter ratio/thresholding, wetland classification)
    will be dispatched as an asynchronous background task / worker here.
    """
    job_id = str(uuid.uuid4())
    # Initial status set to queued/running, with sample result pre-staged for immediate hackathon testing
    jobs_db[job_id] = {
        "job_id": job_id,
        "status": "complete",
        "step": "Sample mock analysis generated",
        "result": load_sample_result()
    }
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {
        "job_id": job_id,
        "status": job.get("status", "queued"),
        "step": job.get("step", "Processing")
    }

@app.get("/results/{job_id}")
def get_result(job_id: str):
    job = jobs_db.get(job_id)
    if not job:
        # If job is not in memory, return the default sample result for seamless testing
        sample = load_sample_result()
        return sample
    
    result = job.get("result")
    if not result:
        raise HTTPException(status_code=400, detail="Result is not ready yet")
    return result

