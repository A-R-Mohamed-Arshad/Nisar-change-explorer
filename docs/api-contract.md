# API Contract (DRAFT)

> **Notice:** This document is **DRAFT**. Exact field names and schema will be frozen at a team meeting. Teammates must adhere to this contract when building client and server components.

---

## 1. General Principles

### 1.1 Error Format
All endpoints return errors in the following single consistent structure:
```json
{
  "error": {
    "code": "404",
    "message": "Job sample-id not found"
  }
}
```

### 1.2 Job Status Values
Job lifecycles transition strictly through the following status values:
- `queued`
- `running`
- `complete`
- `failed`

### 1.3 Mode Field
Every data response indicates its provenance via the `mode` field:
- `sample` (mock / fallback test data)
- `saved` (cached / precomputed dataset)
- `live` (queried from active NASA/ASF APIs or freshly computed)

*Rule: Never present sample data as live.*

---

## 2. Endpoints

### 2.1 Health Check
- **Method:** `GET`
- **Path:** `/health`
- **Request Fields:** None
- **Response Fields:**
  - `ok` (boolean)
```json
{
  "ok": true
}
```

---

### 2.2 Check Availability
- **Method:** `POST`
- **Path:** `/availability`
- **Request Fields:**
  - `area` (object, GeoJSON geometry, optional)
  - `date_range` (object, e.g. `{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}`, optional)
- **Response Fields:**
  - `status` (string, e.g. "complete")
  - `mode` (string: "live", "saved", or "sample")
  - `passes` (array of objects):
    - `granule_id` (string)
    - `date` (string)
    - `orbit_direction` (string)
    - `quality_level` (string)
```json
{
  "status": "complete",
  "mode": "sample",
  "passes": [
    {
      "granule_id": "NISAR_L2_PR_GCOV_001_005_A_123_20241001T000000_20241001T000030_M01_F_J_001.h5",
      "date": "2024-10-01",
      "orbit_direction": "Ascending",
      "quality_level": "nominal"
    }
  ]
}
```

---

### 2.3 Start Analysis
- **Method:** `POST`
- **Path:** `/analyze`
- **Request Fields:**
  - `area` (object, GeoJSON geometry)
  - `dates` (object with `pre_event` and `post_event` strings)
  - `analysis_type` (string, e.g. "flood_wetland")
- **Response Fields:**
  - `job_id` (string, UUID)
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 2.4 Get Job Status
- **Method:** `GET`
- **Path:** `/jobs/{job_id}`
- **Request Fields:** Path parameter `job_id`
- **Response Fields:**
  - `job_id` (string)
  - `status` (string: "queued", "running", "complete", "failed")
  - `step` (string, description of current progress step)
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "step": "Co-registering NISAR L2 GCOV rasters"
}
```

---

### 2.5 Get Analysis Results
- **Method:** `GET`
- **Path:** `/results/{job_id}`
- **Request Fields:** Path parameter `job_id`
- **Response Fields:**
  - `status` (string: "queued", "running", "complete", "failed")
  - `mode` (string: "live", "saved", or "sample")
  - `area` (object, GeoJSON geometry of the area analyzed)
  - `dates_used` (object, pre- and post-event dates used in computation)
  - `files_used` (array of satellite granules used, with `quality_level`)
  - `result_map_url` (string, tile link or raster map overlay URL)
  - `area_changed_by_category` (object, area changed per category in sq km)
  - `confidence` (number, score from 0.0 to 1.0)
  - `confidence_reason` (string, explanation of score)
  - `limits` (string, sensor or algorithm caveats, e.g., layover/shadow)
  - `source_type` (string, sensor and product level)
  - `_note` (string, optional developer/placeholder notes)

```json
{
  "_note": "This is a placeholder sample result for development and offline testing.",
  "status": "complete",
  "mode": "sample",
  "area": {
    "type": "Polygon",
    "coordinates": [
      [
        [79.80, 11.90],
        [80.05, 11.90],
        [80.05, 12.15],
        [79.80, 12.15],
        [79.80, 11.90]
      ]
    ]
  },
  "dates_used": {
    "pre_event": "2024-10-01",
    "post_event": "2024-10-15"
  },
  "files_used": [
    {
      "granule_id": "NISAR_L2_PR_GCOV_001_005_A_123_20241001T000000_20241001T000030_M01_F_J_001.h5",
      "quality_level": "nominal"
    },
    {
      "granule_id": "NISAR_L2_PR_GCOV_001_005_A_123_20241015T000000_20241015T000030_M01_F_J_001.h5",
      "quality_level": "nominal"
    }
  ],
  "result_map_url": "https://example.com/tiles/sample-nisar-change/{z}/{x}/{y}.png",
  "area_changed_by_category": {
    "water_increase_sqkm": 14.25,
    "wetland_loss_sqkm": 2.10,
    "unclassified_change_sqkm": 0.85
  },
  "confidence": 0.88,
  "confidence_reason": "High temporal coherence and optimal baseline angle in sample mock calculation.",
  "limits": "Sample simulation only. Cloud cover does not affect radar, but steep topography may introduce layover distortion.",
  "source_type": "NISAR L2 GCOV (Simulated Sample)"
}
```

