import json
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from server.config import BASE_DIR, SIMULATE_DELAY_SECONDS

SAMPLE_RESULT_PATH = BASE_DIR / "data" / "sample" / "sample-result.json"

def _load_sample_json() -> Dict[str, Any]:
    if SAMPLE_RESULT_PATH.exists():
        with open(SAMPLE_RESULT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "_note": "Fallback sample result (offline placeholder)",
        "status": "complete",
        "mode": "sample",
        "area": None,
        "dates_used": {},
        "files_used": [],
        "result_map_url": "/static/results/placeholder_overlay.png",
        "result_map_bbox": None,
        "area_changed_by_category": {},
        "confidence": 0.0,
        "confidence_reason": "No sample file",
        "limits": "Sample placeholder",
        "source_type": "Sample"
    }

def find_passes(area: Dict[str, float], start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Availability check stub for NISAR passes over a bounding box.
    """
    return [
        {
            "granule_id": "NISAR_L2_PR_GCOV_001_005_A_123_20241001T000000_20241001T000030_M01_F_J_001.h5",
            "date": start_date,
            "track": 123,
            "direction": "Ascending",
            "quality_level": "nominal"
        },
        {
            "granule_id": "NISAR_L2_PR_GCOV_001_005_A_123_20241015T000000_20241015T000030_M01_F_J_001.h5",
            "date": end_date,
            "track": 123,
            "direction": "Ascending",
            "quality_level": "nominal"
        }
    ]

def run_analysis(
    area: Dict[str, float],
    start_date: str,
    end_date: str,
    question: Optional[str] = "flood_wetland",
    progress: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
    """
    Science algorithm interface stub for NISAR Change Detection.
    NOTE: Sanjay will replace this stub with the real science pipeline
    (raster processing, coregistration, backscatter ratio, thresholding).

    INPUT CONTRACT:
        - area: Dict[str, float] with keys 'west', 'south', 'east', 'north' (bounding box coordinates)
        - start_date: str, formatted as 'YYYY-MM-DD' (pre-event date)
        - end_date: str, formatted as 'YYYY-MM-DD' (post-event date)
        - question: Optional[str], type of change analysis requested (default: 'flood_wetland')
        - progress: Optional[Callable[[str], None]], callback taking step messages in standard order:
                    1. "Finding passes"
                    2. "Fetching data"
                    3. "Comparing dates"
                    4. "Saving result"
    """
    steps = [
        "Finding passes",
        "Fetching data",
        "Comparing dates",
        "Saving result"
    ]

    for step in steps:
        if progress:
            progress(step)
        if SIMULATE_DELAY_SECONDS > 0:
            time.sleep(SIMULATE_DELAY_SECONDS)

    sample = _load_sample_json()
    # Inject requested area and dates into the sample output
    sample["area"] = area
    sample["dates_used"] = {
        "pre_event": start_date,
        "post_event": end_date
    }
    sample["mode"] = "sample"
    sample["status"] = "complete"
    sample["result_map_url"] = "/static/results/placeholder_overlay.png"
    sample["result_map_bbox"] = area
    return sample
