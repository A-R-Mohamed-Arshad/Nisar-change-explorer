import sys
from pathlib import Path

# Ensure repo root is always in sys.path
_repo_root = Path(__file__).resolve().parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from unittest.mock import patch
from fastapi.testclient import TestClient

from server.main import app, _execute_analysis_background
from server.caching import compute_cache_key, save_result_to_cache
from server.jobs import get_job_record, create_job_record

# Fast in-memory client
client = TestClient(app)

SAMPLE_BBOX = {"west": 79.80, "south": 11.90, "east": 80.00, "north": 12.10}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

def test_availability_fallback_to_sample():
    res = client.post("/availability", json={
        "area": SAMPLE_BBOX,
        "start_date": "2024-10-01",
        "end_date": "2024-10-15"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "complete"
    assert data["mode"] == "sample"
    assert len(data["passes"]) >= 2
    assert "usable_pass_count" in data

def test_analyze_returns_job_id_immediately():
    res = client.post("/analyze", json={
        "area": SAMPLE_BBOX,
        "start_date": "2024-10-01",
        "end_date": "2024-10-15",
        "question": "flood_wetland"
    })
    assert res.status_code == 200
    data = res.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)

def test_job_reaches_complete_and_result_returned():
    job_id = "test-job-complete-123"
    create_job_record(job_id)

    cache_key = compute_cache_key(SAMPLE_BBOX, "2024-10-01", "2024-10-15", "flood_wetland")
    _execute_analysis_background(
        job_id=job_id,
        area=SAMPLE_BBOX,
        start_date="2024-10-01",
        end_date="2024-10-15",
        question="flood_wetland",
        cache_key=cache_key
    )

    job_res = client.get(f"/jobs/{job_id}")
    assert job_res.status_code == 200
    job_data = job_res.json()
    assert job_data["status"] == "complete"
    assert job_data["step"] == "Saving result"

    res = client.get(f"/results/{job_id}")
    assert res.status_code == 200
    result_data = res.json()
    assert result_data["status"] == "complete"
    assert result_data["mode"] == "sample"
    assert "result_map_url" in result_data
    assert "confidence" in result_data

def test_cache_hit_returns_mode_saved():
    area = {"west": 79.85, "south": 11.95, "east": 80.05, "north": 12.05}
    start_date = "2024-09-01"
    end_date = "2024-09-15"
    question = "coastal_flood"

    key = compute_cache_key(area, start_date, end_date, question)
    save_result_to_cache(key, {
        "status": "complete",
        "mode": "sample",
        "area": area,
        "dates_used": {"pre_event": start_date, "post_event": end_date},
        "files_used": [],
        "result_map_url": "/static/results/placeholder_overlay.png",
        "confidence": 0.95
    })

    res = client.post("/analyze", json={
        "area": area,
        "start_date": start_date,
        "end_date": end_date,
        "question": question
    })
    assert res.status_code == 200
    job_id = res.json()["job_id"]
    assert res.json()["cached"] is True

    result_res = client.get(f"/results/{job_id}")
    assert result_res.status_code == 200
    assert result_res.json()["mode"] == "saved"

def test_error_area_too_large():
    huge_bbox = {"west": 75.0, "south": 10.0, "east": 76.5, "north": 11.5}
    res = client.post("/analyze", json={
        "area": huge_bbox,
        "start_date": "2024-10-01",
        "end_date": "2024-10-15"
    })
    assert res.status_code == 400
    err = res.json()
    assert "error" in err
    assert err["error"]["code"] == "AREA_TOO_LARGE"
    assert "exceeds maximum limit" in err["error"]["message"]

def test_error_insufficient_data():
    job_id = "test-job-insufficient"
    create_job_record(job_id)

    with patch("server.main.query_availability") as mock_avail:
        mock_avail.return_value = {
            "status": "complete",
            "mode": "sample",
            "passes": [{"granule_id": "SINGLE_PASS_01", "date": "2024-10-01"}]
        }
        _execute_analysis_background(
            job_id=job_id,
            area=SAMPLE_BBOX,
            start_date="2024-10-01",
            end_date="2024-10-15",
            question="flood_wetland",
            cache_key="key-insufficient"
        )

    job_rec = get_job_record(job_id)
    assert job_rec["status"] == "failed"
    assert job_rec["error"]["code"] == "INSUFFICIENT_DATA"

    res = client.get(f"/results/{job_id}")
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "INSUFFICIENT_DATA"

def test_error_invalid_request():
    res = client.post("/analyze", json={"question": "flood"})
    assert res.status_code == 400
    err = res.json()
    assert "error" in err
    assert err["error"]["code"] == "INVALID_REQUEST"

def test_error_shape_consistent_everywhere():
    res = client.get("/jobs/non-existent-uuid")
    assert res.status_code == 404
    err = res.json()
    assert "error" in err
    assert "code" in err["error"]
    assert "message" in err["error"]
