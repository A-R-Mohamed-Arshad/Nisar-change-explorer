import math
from typing import Any, Dict, Tuple
from fastapi import HTTPException
from server.config import MAX_AREA_KM

def parse_and_validate_area(area_input: Any) -> Dict[str, float]:
    """
    Validates and normalizes bounding box input into {west, south, east, north}.
    Accepts:
      - dict with west, south, east, north
      - GeoJSON Polygon or bbox array
    """
    if not isinstance(area_input, dict):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_REQUEST",
                "message": "Field 'area' must be a dictionary specifying a bounding box or GeoJSON geometry. Please provide {west, south, east, north}."
            }
        )

    # Direct {west, south, east, north}
    if all(k in area_input for k in ("west", "south", "east", "north")):
        try:
            west = float(area_input["west"])
            south = float(area_input["south"])
            east = float(area_input["east"])
            north = float(area_input["north"])
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_REQUEST",
                    "message": "Bounding box coordinates must be valid floating point numbers."
                }
            )
    # GeoJSON Polygon fallback
    elif area_input.get("type") == "Polygon" and "coordinates" in area_input:
        try:
            coords = area_input["coordinates"][0]
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            west, east = min(lons), max(lons)
            south, north = min(lats), max(lats)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_REQUEST",
                    "message": "Malformed GeoJSON Polygon coordinates. Please verify your polygon geometry."
                }
            )
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_REQUEST",
                "message": "Missing required bounding box keys: 'west', 'south', 'east', 'north'. Please check your request parameters."
            }
        )

    # Basic range validity
    if not (-180.0 <= west <= 180.0 and -180.0 <= east <= 180.0 and -90.0 <= south <= 90.0 and -90.0 <= north <= 90.0):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_REQUEST",
                "message": "Coordinates out of bounds (-180 to 180 for longitude, -90 to 90 for latitude). Please check your coordinates."
            }
        )
    if west > east or south > north:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_REQUEST",
                "message": "Invalid coordinates: 'west' must be <= 'east' and 'south' must be <= 'north'."
            }
        )

    # Check area size against MAX_AREA_KM
    width_km, height_km = calculate_bbox_dimensions_km(west, south, east, north)
    if width_km > MAX_AREA_KM or height_km > MAX_AREA_KM:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "AREA_TOO_LARGE",
                "message": f"Requested area ({width_km:.1f} km x {height_km:.1f} km) exceeds maximum limit of {MAX_AREA_KM:.1f} km x {MAX_AREA_KM:.1f} km. Please select a smaller bounding box."
            }
        )

    return {"west": west, "south": south, "east": east, "north": north}

def calculate_bbox_dimensions_km(west: float, south: float, east: float, north: float) -> Tuple[float, float]:
    """
    Calculates approx width and height of bbox in kilometers using haversine formula.
    """
    avg_lat = (south + north) / 2.0
    lat_rad = math.radians(avg_lat)
    # Approx 111.32 km per degree of latitude
    height_km = abs(north - south) * 110.574
    # Longitude shrinks by cos(latitude)
    width_km = abs(east - west) * (111.320 * math.cos(lat_rad))
    return width_km, height_km
