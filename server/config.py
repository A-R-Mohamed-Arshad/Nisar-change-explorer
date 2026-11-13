import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for the repository root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from repo root if it exists
load_dotenv(BASE_DIR / ".env")

# Earthdata & NASA Credentials (loaded strictly from environment)
EARTHDATA_USERNAME = os.getenv("EARTHDATA_USERNAME", "")
EARTHDATA_PASSWORD = os.getenv("EARTHDATA_PASSWORD", "")
AI_API_KEY = os.getenv("AI_API_KEY", "")

# Allowed CORS origins
ALLOWED_ORIGINS_RAW = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [
    origin.strip() for origin in ALLOWED_ORIGINS_RAW.split(",") if origin.strip()
] or ["http://localhost:5173"]

# Cache and Storage Directory
CACHE_DIR_PATH = os.getenv("CACHE_DIR", str(BASE_DIR / "cache"))
CACHE_DIR = Path(CACHE_DIR_PATH)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Sub-directories under CACHE_DIR
RESULTS_DIR = CACHE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MAPS_DIR = CACHE_DIR / "maps"
MAPS_DIR.mkdir(parents=True, exist_ok=True)

JOBS_STORAGE_FILE = CACHE_DIR / "jobs.json"

# Science and Validation parameters
MAX_AREA_KM = float(os.getenv("MAX_AREA_KM", "25"))

# Simulation parameters (e.g. realistic progress pacing for UI testing)
SIMULATE_DELAY_SECONDS = float(os.getenv("SIMULATE_DELAY_SECONDS", "0"))

# NASA / NISAR Dataset Constants & Collection Identifiers
# TODO: Confirm official NISAR CMR collection short names and concept IDs once publicly assigned
# e.g., 'NISAR_L2_PR_GCOV', 'NISAR_L1_PR_RSLC', etc.
NISAR_COLLECTION_SHORT_NAME = "TODO_CONFIRM_NISAR_COLLECTION_SHORT_NAME"
NISAR_CONCEPT_ID = "TODO_CONFIRM_NISAR_CONCEPT_ID"
NISAR_DEFAULT_PLATFORM = "NISAR"
