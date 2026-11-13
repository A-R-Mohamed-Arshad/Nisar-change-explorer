import json
import logging
from typing import Any, Dict, Optional
from server.config import JOBS_STORAGE_FILE

logger = logging.getLogger("jobs")

# In-memory job repository
# job_id -> {"job_id": str, "status": str, "step": str, "result": dict, "error": dict}
jobs_store: Dict[str, Dict[str, Any]] = {}

def load_jobs_from_disk() -> None:
    """Load persistent job records from CACHE_DIR/jobs.json if present."""
    global jobs_store
    if JOBS_STORAGE_FILE.exists():
        try:
            with open(JOBS_STORAGE_FILE, "r", encoding="utf-8") as f:
                jobs_store = json.load(f)
            logger.info("Loaded %d jobs from %s", len(jobs_store), JOBS_STORAGE_FILE)
        except Exception as exc:
            logger.warning("Could not read jobs storage file: %s", exc)

def save_jobs_to_disk() -> None:
    """Persist all in-memory jobs to CACHE_DIR/jobs.json."""
    try:
        with open(JOBS_STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs_store, f, indent=2)
    except Exception as exc:
        logger.warning("Could not persist jobs to disk: %s", exc)

def get_job_record(job_id: str) -> Optional[Dict[str, Any]]:
    return jobs_store.get(job_id)

def create_job_record(job_id: str) -> Dict[str, Any]:
    record = {
        "job_id": job_id,
        "status": "queued",
        "step": "Finding passes",
        "result": None,
        "error": None
    }
    jobs_store[job_id] = record
    save_jobs_to_disk()
    return record

def update_job_step(job_id: str, step_message: str) -> None:
    if job_id in jobs_store:
        jobs_store[job_id]["status"] = "running"
        jobs_store[job_id]["step"] = step_message
        save_jobs_to_disk()

def complete_job(job_id: str, result: Dict[str, Any]) -> None:
    if job_id in jobs_store:
        jobs_store[job_id]["status"] = "complete"
        jobs_store[job_id]["step"] = "Saving result"
        jobs_store[job_id]["result"] = result
        save_jobs_to_disk()

def fail_job(job_id: str, code: str, message: str) -> None:
    if job_id in jobs_store:
        jobs_store[job_id]["status"] = "failed"
        jobs_store[job_id]["step"] = "Failed"
        jobs_store[job_id]["error"] = {"code": code, "message": message}
        save_jobs_to_disk()
