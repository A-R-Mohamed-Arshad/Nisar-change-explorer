# NISAR Change Explorer

A map web application where users pick an area, inspect what NASA/ISRO NISAR radar data exists, run change analyses (such as flood inundation and wetland change), and inspect labeled results with confidence metrics, scientific limitations, and raster map overlays.

Built for a hackathon team of 6 with simple interfaces, clean separation of concerns, and robust error handling.

---

## Architecture & Tech Stack

- **Frontend (`web/`)**: React (Vite), MapLibre GL JS (full-screen map with OpenStreetMap basemap & NASA GIBS raster overlay), Chart.js.
  - Components: `ProgressDisplay`, `BeforeAfterSlider`, `DataModeBadge`.
  - Unified client: `web/src/api.js` (with automatic fallback to `sample-result.json` if offline).
- **Backend (`server/`)**: Python FastAPI, Uvicorn, BackgroundTasks worker, disk & memory caching, Earthdata & ASF search integration (`asf_search`, `earthaccess`).
- **Data & Contract (`data/sample/`, `docs/`)**: Sample benchmark outputs, demo areas list, and API contract specification.

---

## Repository Structure

```
Nisar-change-explorer/
├── .env.example              # Template for environment variables (never commit secrets)
├── .gitignore                # Git ignore rules for node, python, dist, and secrets
├── README.md                 # Project documentation and quick start
├── vercel.json               # Vercel deployment configuration
├── .github/
│   └── pull_request_template.md # Standard PR template for teammates
├── data/
│   ├── demo_areas.json       # Demo areas for cache precomputation
│   └── sample/
│       └── sample-result.json# Standard benchmark sample result
├── docs/
│   ├── api-contract.md       # API contract specification (DRAFT)
│   ├── deploy.md             # Complete cloud, Docker & tunnel deployment guide
│   └── HANDOVER_TEMPLATE.md  # Standard teammate shift handover template
├── server/
│   ├── main.py               # FastAPI application with CORS and background task pipeline
│   ├── config.py             # Server configuration & environment loading
│   ├── science.py            # Science algorithm stub (contract for Sanjay)
│   ├── availability.py       # Live catalog search with safe fallback
│   ├── caching.py            # Result caching keyed by stable hash
│   ├── jobs.py               # Job state persistence (survives server restarts)
│   ├── validation.py         # GeoJSON and bounding box validation
│   ├── precompute.py         # Script to precompute and fill cache for demo areas
│   ├── requirements.txt      # Production Python dependencies
│   ├── requirements-dev.txt  # Dev/test dependencies (pytest, httpx2)
│   ├── Dockerfile            # Production Docker container
│   ├── static/maps/          # Static map overlay placeholders
│   └── tests/
│       ├── conftest.py       # Test configuration and path setup
│       └── test_server.py    # Pytest test suite (9 test cases)
└── web/
    ├── public/
    │   └── sample-result.json# Public fallback sample result
    ├── src/
    │   ├── api.js            # Unified API client with automatic offline fallback
    │   ├── App.jsx           # Main map UI with GIBS toggle & DataModeBadge
    │   ├── config.js         # GIBS tile and layer configuration
    │   ├── components/
    │   │   ├── DataModeBadge.jsx     # LIVE / SAVED / SAMPLE indicator
    │   │   ├── ProgressDisplay.jsx   # Polls job status with plain step messages
    │   │   ├── BeforeAfterSlider.jsx # Swipe comparison between before & after
    │   │   └── ComponentPreview.jsx  # Story-style demo component preview
    │   └── main.jsx          # React DOM entrypoint
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## Golden Rule

> **Never present sample data as live.**  
> Every response carries a `mode` of `"live"`, `"saved"`, or `"sample"`.  
> The web client displays a badge indicating the current data status (`LIVE DATA`, `SAVED / CACHED`, or `SAMPLE DATA`).

---

## Getting Started

### 1. Environment Setup

Copy `.env.example` to `.env` in the repository root:
```bash
cp .env.example .env
```
> **Security Reminder:** Never commit real credentials or API keys.

---

### 2. Running the Frontend (`web/`)

```bash
cd web
npm install
npm run dev
```

The frontend will start at `http://localhost:5173`.
- By default, it connects to `http://localhost:8000`.
- If the server is offline or unreachable, `web/src/api.js` falls back to `/sample-result.json` seamlessly and displays the **SAMPLE DATA** badge.

---

### 3. Running the Server (`server/`)

On **Windows (Command Prompt / PowerShell)**:
```cmd
cd server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

On **macOS / Linux**:
```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The server runs at `http://localhost:8000`.
- Health check: `http://localhost:8000/health`
- Interactive Swagger docs: `http://localhost:8000/docs`

---

### 4. Running Server Tests

To execute the automated test suite:
```bash
cd server
pip install -r requirements-dev.txt
pytest
```
All 9 test cases cover health check, catalog fallback, background execution, cache hit detection, area size validation, insufficient data detection, and uniform error formats.

---

### 5. Running the Precompute Script

To pre-fill the cache with demo scenarios:
```bash
cd server
python precompute.py
```
This reads coordinates and dates from `data/demo_areas.json` and populates `cache/results/` so demo presentations return instantaneous results with `mode: "saved"`.

---

## Known Issues & Notes

1. **NISAR Mission Launch & Official Granule IDs**:
   - The NASA GIBS NISAR layer ID and CMR collection names are pending operational broadcast. Placeholders (`TODO_CONFIRM_...`) are intentionally used in `server/config.py` and `web/src/config.js`. The app operates cleanly in sample/offline fallback mode when live identifiers are not yet active.
2. **Network Timeouts on Pre-built Binary Wheels**:
   - Downloading large binary wheels (such as `numpy` or `shapely`) over constrained network links may occasionally trigger pip timeouts. If encountered, use:
     ```bash
     pip install --default-timeout=300 --retries 10 -r requirements.txt
     ```
