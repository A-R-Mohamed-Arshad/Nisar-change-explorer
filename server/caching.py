import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from server.config import RESULTS_DIR

logger = logging.getLogger("cache")

def compute_cache_key(
    area: Dict[str, float],
    start_date: str,
    end_date: str,
    question: Optional[str] = "flood_wetland"
) -> str:
    """
    Computes a deterministic hash key from rounded bounding box (3 decimals ~ 100m precision),
    start date, end date, and question.
    """
    w = round(area["west"], 3)
    s = round(area["south"], 3)
    e = round(area["east"], 3)
    n = round(area["north"], 3)
    payload = f"{w}_{s}_{e}_{n}:{start_date}:{end_date}:{question or 'default'}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def get_cached_result(cache_key: str) -> Optional[Dict[str, Any]]:
    result_file = RESULTS_DIR / f"{cache_key}.json"
    if result_file.exists():
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["mode"] = "saved"
            return data
        except Exception as exc:
            logger.warning("Error reading cache file %s: %s", result_file, exc)
    return None

def save_result_to_cache(cache_key: str, result_data: Dict[str, Any]) -> Path:
    result_file = RESULTS_DIR / f"{cache_key}.json"
    try:
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2)
    except Exception as exc:
        logger.warning("Error writing cache file %s: %s", result_file, exc)
    return result_file
