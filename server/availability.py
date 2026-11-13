import logging
from typing import Any, Dict, List, Optional
from server.config import (
    EARTHDATA_USERNAME,
    EARTHDATA_PASSWORD,
    NISAR_COLLECTION_SHORT_NAME,
    NISAR_CONCEPT_ID,
    NISAR_DEFAULT_PLATFORM
)
from server.science import find_passes as science_find_passes

logger = logging.getLogger("availability")

def query_availability(
    area: Dict[str, float],
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Queries catalogue for available NISAR passes without downloading data.
    Attempts asf_search and/or earthaccess if installed and configured.
    Safely falls back to mode 'sample' with a clear reason if upstream call fails
    or NISAR dataset search is not yet supported. Never crashes.
    """
    # Attempt catalogue search via asf_search or earthaccess
    passes: List[Dict[str, Any]] = []
    mode = "sample"
    reason: Optional[str] = None

    try:
        # Check if asf_search is available in environment
        import asf_search as asf  # type: ignore

        # Validate if NISAR constants or search options are supported by the installed library version
        # We do not guess or invent constants; we inspect what the library provides.
        w, s, e, n = area["west"], area["south"], area["east"], area["north"]
        wkt_polygon = f"POLYGON(({w} {s}, {e} {s}, {e} {n}, {w} {n}, {w} {s}))"

        # Check if ASF search has NISAR platform constant
        platform = None
        if hasattr(asf, "PLATFORM"):
            for attr in dir(asf.PLATFORM):
                if "NISAR" in attr.upper():
                    platform = getattr(asf.PLATFORM, attr)
                    break

        if platform is None:
            # Fallback check on string constant if defined in config
            if NISAR_COLLECTION_SHORT_NAME != "TODO_CONFIRM_NISAR_COLLECTION_SHORT_NAME":
                platform = NISAR_DEFAULT_PLATFORM

        if platform:
            logger.info("Executing asf_search query for platform: %s", platform)
            results = asf.geo_search(
                intersectsWith=wkt_polygon,
                platform=platform,
                start=start_date,
                end=end_date,
            )
            for res in results:
                props = getattr(res, "properties", {})
                quality = props.get("quality_level") or props.get("processingLevel") or "nominal"
                passes.append({
                    "granule_id": props.get("fileID") or props.get("sceneName") or str(res),
                    "date": props.get("startTime", "")[:10] if props.get("startTime") else start_date,
                    "track": props.get("pathNumber"),
                    "direction": props.get("flightDirection", "Ascending"),
                    "quality_level": quality
                })
            mode = "live"
        else:
            reason = "asf_search does not currently define a NISAR platform constant; using sample passes."
    except ImportError:
        reason = "asf_search is not installed in current environment; catalog query using fallback sample data."
    except Exception as exc:
        logger.warning("Upstream catalogue query error: %s", exc)
        reason = f"Upstream search error: {str(exc)}; using sample passes."

    # If live search didn't yield results or fell back, populate sample passes
    if mode != "live" or not passes:
        sample_passes = science_find_passes(area, start_date, end_date)
        return {
            "status": "complete",
            "mode": "sample",
            "reason": reason or "Sample fallback passes provided.",
            "passes": sample_passes,
            "usable_pass_count": len(sample_passes)
        }

    return {
        "status": "complete",
        "mode": "live",
        "passes": passes,
        "usable_pass_count": len(passes)
    }
