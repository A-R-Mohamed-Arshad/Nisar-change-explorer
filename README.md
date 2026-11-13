# NISAR Change Explorer

A map web application where users can select an area of interest, check available NASA/ISRO NISAR radar passes, trigger change analysis (such as flood inundation and wetland change), and view labeled results with confidence scores and limitations.

Built for a hackathon team of 6 with simplicity, clean interfaces, and clear documentation in mind.

---

## Architecture & Tech Stack

- **Frontend (`web/`)**: React (Vite), MapLibre GL JS (full-screen map with OpenStreetMap basemap & NASA GIBS raster overlay), Chart.js.
- **Backend (`server/`)**: Python FastAPI, Uvicorn, Earthdata & ASF search libraries (`earthaccess`, `asf_search`).
- **Data & Contract (`data/sample/`, `docs/`)**: Sample benchmark outputs and draft API contract.

---

## Repository Structure

```
Nisar-change-explorer/
├── .env.example              # Template for environment variables (never commit secrets)
├── .gitignore                # Git ignore rules for node, python, dist, and secrets
├── README.md                 # Project documentation and quick start
├── data/
│   └── sample/
│       └── sample-result.json# Standard benchmark sample result
├── docs/
│   └── api-contract.md       # API contract specification (DRAFT)
├── server/
│   ├── main.py               # FastAPI application with CORS and mock endpoints
│   └── requirements.txt      # Python dependencies
└── web/
    ├── public/
    │   └── sample-result.json# Public fallback sample result
    ├── src/
    │   ├── api.js            # Unified API client with automatic offline fallback
    │   ├── App.jsx           # Main map UI with GIBS toggle & sample badge
    │   ├── config.js         # GIBS tile and layer configuration
    │   └── main.jsx          # React DOM entrypoint
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## Golden Rule

> **Never present sample data as live.**  
> Any simulated, mock, or fallback data must clearly indicate `mode: "sample"`, and the UI displays a `SAMPLE DATA` badge accordingly.

---

## Getting Started

### 1. Environment Setup

Copy `.env.example` to `.env` in the repository root (or as needed by your sub-environment):
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

The server will be available at `http://localhost:8000`.
- Health check: `http://localhost:8000/health`
- Interactive Swagger docs: `http://localhost:8000/docs`

