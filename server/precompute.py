"""
Precompute script to pre-fill the cache for demo areas.
Reads entries from data/demo_areas.json and executes run_analysis,
saving results under CACHE_DIR/results/.
"""

import json
import logging
from pathlib import Path
from server.config import BASE_DIR
from server.science import run_analysis
from server.caching import compute_cache_key, save_result_to_cache
from server.validation import parse_and_validate_area

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("precompute")

DEMO_AREAS_FILE = BASE_DIR / "data" / "demo_areas.json"

def run_precompute():
    if not DEMO_AREAS_FILE.exists():
        logger.warning("No demo areas file found at %s", DEMO_AREAS_FILE)
        return

    with open(DEMO_AREAS_FILE, "r", encoding="utf-8") as f:
        demo_areas = json.load(f)

    logger.info("Found %d demo areas to precompute", len(demo_areas))

    for item in demo_areas:
        if not isinstance(item, dict) or "area" not in item:
            continue
        try:
            area = parse_and_validate_area(item["area"])
            start_date = item.get("start_date", "2024-10-01")
            end_date = item.get("end_date", "2024-10-15")
            question = item.get("question", "flood_wetland")

            cache_key = compute_cache_key(area, start_date, end_date, question)
            logger.info("Precomputing: %s (key: %s)", item.get("name", "Demo Area"), cache_key)

            result = run_analysis(
                area=area,
                start_date=start_date,
                end_date=end_date,
                question=question,
                progress=lambda msg: logger.info("  Step: %s", msg)
            )
            # Mark cached result as saved
            result["mode"] = "saved"
            save_result_to_cache(cache_key, result)
            logger.info("  Saved to cache successfully.")
        except Exception as exc:
            logger.error("Error precomputing %s: %s", item.get("name", "Demo"), exc)

if __name__ == "__main__":
    run_precompute()
