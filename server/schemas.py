from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Common / Shared Models
# ---------------------------------------------------------------------------

class BoundingBox(BaseModel):
    west: float = Field(..., ge=-180.0, le=180.0, description="Western longitude")
    south: float = Field(..., ge=-90.0, le=90.0, description="Southern latitude")
    east: float = Field(..., ge=-180.0, le=180.0, description="Eastern longitude")
    north: float = Field(..., ge=-90.0, le=90.0, description="Northern latitude")

class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Plain-language error description with guidance")

class ErrorResponse(BaseModel):
    error: ErrorDetail

class HealthResponse(BaseModel):
    ok: bool = True

# ---------------------------------------------------------------------------
# Availability Endpoint Models
# ---------------------------------------------------------------------------

class AvailabilityRequest(BaseModel):
    area: Any = Field(..., description="Bounding box dict {west, south, east, north} or GeoJSON Polygon")
    start_date: Optional[str] = Field("2024-10-01", description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field("2024-10-15", description="End date (YYYY-MM-DD)")

class SatellitePass(BaseModel):
    granule_id: str = Field(..., description="Identifier of the satellite granule")
    date: str = Field(..., description="Observation date (YYYY-MM-DD)")
    track: Optional[int] = Field(None, description="Orbit track / path number")
    direction: Optional[str] = Field("Ascending", description="Orbit pass direction (Ascending / Descending)")
    quality_level: Optional[str] = Field("nominal", description="Data product quality level (BETA, PROVISIONAL, VALIDATED, nominal)")

class AvailabilityResponse(BaseModel):
    status: Literal["complete", "failed"] = "complete"
    mode: Literal["live", "saved", "sample"] = "sample"
    reason: Optional[str] = Field(None, description="Explanation when operating in sample or fallback mode")
    passes: List[SatellitePass] = Field(default_factory=list, description="Available satellite passes")
    usable_pass_count: int = Field(0, description="Total number of usable passes found")

# ---------------------------------------------------------------------------
# Analysis & Job Endpoint Models
# ---------------------------------------------------------------------------

class AnalysisDates(BaseModel):
    pre_event: Optional[str] = None
    post_event: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None

class AnalysisRequest(BaseModel):
    area: Any = Field(..., description="Bounding box dict {west, south, east, north} or GeoJSON Polygon")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    dates: Optional[AnalysisDates] = None
    question: Optional[str] = "flood_wetland"
    analysis_type: Optional[str] = None

class AnalysisResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier (UUID)")
    cached: bool = Field(False, description="True if analysis was immediately retrieved from cache")

class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "complete", "failed"]
    step: str = Field(..., description="Current progress step description")
    error: Optional[ErrorDetail] = None

# ---------------------------------------------------------------------------
# Results Endpoint Models
# ---------------------------------------------------------------------------

class GranuleUsed(BaseModel):
    granule_id: str
    quality_level: Optional[str] = "nominal"

class DatesUsed(BaseModel):
    pre_event: str
    post_event: str

class ResultResponse(BaseModel):
    status: Literal["complete", "failed"] = "complete"
    mode: Literal["live", "saved", "sample"] = "sample"
    area: Any = Field(..., description="Bounding box or GeoJSON geometry evaluated")
    dates_used: DatesUsed = Field(..., description="Pre- and post-event observation dates used")
    files_used: List[GranuleUsed] = Field(default_factory=list, description="Satellite files used in analysis")
    result_map_url: str = Field(..., description="URL to rendered change overlay image")
    result_map_bbox: Optional[Any] = Field(None, description="Bounding box alignment coordinates for map overlay")
    area_changed_by_category: Dict[str, float] = Field(default_factory=dict, description="Change extent in sq km per category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    confidence_reason: str = Field(..., description="Explanation supporting confidence score")
    limits: str = Field(..., description="Scientific caveats, radar distortions, and limitations")
    source_type: str = Field(..., description="Sensor and processing level specification")
    note: Optional[str] = Field(None, alias="_note", description="Developer or mock notes")

# ---------------------------------------------------------------------------
# System Status Endpoint Model (Task 8)
# ---------------------------------------------------------------------------

class SystemStatusResponse(BaseModel):
    server_version: str
    uptime_seconds: float
    cache_size: int
    earthdata_configured: bool
