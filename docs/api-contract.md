# API Contract (DRAFT)

> **Notice:** This document is **DRAFT**. Exact field names and schema will be frozen at a team meeting. Teammates must adhere to this contract when building client and server components.

---

## 1. General Principles

### 1.1 Error Format
All endpoints return errors in a single consistent structure across the backend:
```json
{
  "error": {
    "code": "AREA_TOO_LARGE",
    "message": "Requested area (32.0 km x 28.0 km) exceeds maximum limit of 25.0 km x 25.0 km. Please select a smaller bounding box."
  }
}
```

Standard error codes:
- `AREA_TOO_LARGE`: Bounding box exceeds maximum allowed dimensions (`MAX_AREA_KM`).
- `INSUFFICIENT_DATA`: Fewer than 2 usable satellite passes available in the date range.
- `NO_DATA`: No satellite passes found for the target area.
- `UPSTREAM_FAILURE`: External API call (NASA CMR, ASF, or science algorithm) failed or timed out.
- `INVALID_REQUEST`: Missing, malformed, or out-of-range request parameters.
- `404`: Requested job or result record not found.

### 1.2 Job Lifecycle & Status Values
Job lifecycles transition strictly through the following status values:
- `queued`
- `running`
- `complete`
- `failed`

### 1.3 Step Messages
During execution, `GET /jobs/{job_id}` reports progress through standardized step messages in this exact order:
1. `"Finding passes"`
2. `"Fetching data"`
3. `"Comparing dates"`
4. `"Saving result"`

### 1.4 Mode Field
Every data response indicates its provenance via the `mode` field:
- `sample`: mock / fallback synthetic dataset.
- `saved`: cached / precomputed output (instantly served from cache).
- `live`: freshly queried from active NASA/ASF APIs or executed by the science pipeline.

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
  - `area` (object, required: bounding box `{west, south, east, north}` in degrees)
  - `start_date` (string, optional: `YYYY-MM-DD`, default: "2024-10-01")
  - `end_date` (string, optional: `YYYY-MM-DD`, default: "2024-10-15")
- **Response Fields:**
  - `status` (string, e.g. "complete")
  - `mode` (string: "live", "saved", or "sample")
  - `passes` (array of objects):
    - `granule_id` (string)
    - `date` (string, `YYYY-MM-DD`)
    - `track` (integer or null, orbit path number)
    - `direction` (string, "Ascending" or "Descending")
    - `quality_level` (string, e.g. "BETA", "PROVISIONAL", "VALIDATED", or "nominal")
  - `usable_pass_count` (integer, count of usable passes)
  - `reason` (string, optional explanation if fell back to sample mode)
```json
{
  "status": "complete",
  "mode": "sample",
  "reason": "asf_search does not currently define a NISAR platform constant; using sample passes.",
  "passes": [
    {
      "granule_id": "NISAR_L2_PR_GCOV_001_005_A_123_20241001T000000_20241001T000030_M01_F_J_001.h5",
      "date": "2024-10-01",
      "track": 123,
      "direction": "Ascending",
      "quality_level": "nominal"
    },
    {
      "granule_id": "NISAR_L2_PR_GCOV_001_005_A_123_20241015T000000_20241015T000030_M01_F_J_001.h5",
      "date": "2024-10-15",
      "track": 123,
      "direction": "Ascending",
      "quality_level": "nominal"
    }
  ],
  "usable_pass_count": 2
}
```

---

### 2.3 Start Analysis
- **Method:** `POST`
- **Path:** `/analyze`
- **Request Fields:**
  - `area` (object, required: bounding box `{west, south, east, north}`)
  - `start_date` (string: `YYYY-MM-DD`)
  - `end_date` (string: `YYYY-MM-DD`)
  - `dates` (object, optional alternative: `{"pre_event": "YYYY-MM-DD", "post_event": "YYYY-MM-DD"}`)
  - `question` (string, optional: type of analysis, default: "flood_wetland")
- **Response Fields:**
  - `job_id` (string, UUID)
  - `cached` (boolean, true if immediately served from cache)
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "cached": false
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
  - `step` (string: current progress message)
  - `error` (object, optional: `{code, message}` present if failed)
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "step": "Comparing dates"
}
```

---

### 2.5 Get Analysis Results
- **Method:** `GET`
- **Path:** `/results/{job_id}`
- **Request Fields:** Path parameter `job_id`
- **Response Fields:**
  - `status` (string: "complete", "failed")
  - `mode` (string: "live", "saved", or "sample")
  - `area` (object, bounding box `{west, south, east, north}`)
  - `dates_used` (object with `pre_event` and `post_event`)
  - `files_used` (array of satellite granules used with `granule_id` and `quality_level`)
  - `result_map_url` (string, URL serving the overlay image, e.g. `/static/results/placeholder_overlay.png`)
  - `result_map_bbox` (object, bounding box `{west, south, east, north}` needed for map alignment)
  - `area_changed_by_category` (object, sq km changed per category)
  - `confidence` (number: 0.0 to 1.0)
  - `confidence_reason` (string, justification for confidence score)
  - `limits` (string, scientific caveats or radar distortions)
  - `source_type` (string, product type)
  - `_note` (string, optional developer/placeholder notes)

```json
{
  "_note": "This is a placeholder sample result for development and offline testing.",
  "status": "complete",
  "mode": "sample",
  "area": {
    "west": 79.80,
    "south": 11.90,
    "east": 80.00,
    "north": 12.10
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
  "result_map_url": "/static/results/placeholder_overlay.png",
  "result_map_bbox": {
    "west": 79.80,
    "south": 11.90,
    "east": 80.00,
    "north": 12.10
  },
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

---

### 2.6 Static Map Overlays
- **Method:** `GET`
- **Path:** `/static/results/{filename}`
- Returns PNG raster overlay image directly from `CACHE_DIR/maps/`.
