"""Traffic-aware drive time via the Google Maps Distance Matrix API."""
from __future__ import annotations

import httpx

DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


class DriveTimeResult(dict):
    """Plain dict with a `status` key: ok | needs_key | error."""


async def fetch_drive_time(
    origin: str,
    destination: str,
    api_key: str,
) -> DriveTimeResult:
    """`origin`/`destination` are anything Google accepts: an address or "lat,lon"."""
    if not api_key:
        return DriveTimeResult(status="needs_key")

    params = {
        "origins": origin,
        "destinations": destination,
        "departure_time": "now",          # required for live-traffic duration
        "traffic_model": "best_guess",
        "units": "metric",
        "key": api_key,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(DISTANCE_MATRIX_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:  # network / timeout
        return DriveTimeResult(status="error", error=str(exc))

    if data.get("status") != "OK":
        return DriveTimeResult(status="error", error=data.get("error_message", data.get("status")))

    try:
        el = data["rows"][0]["elements"][0]
    except (KeyError, IndexError):
        return DriveTimeResult(status="error", error="no route element")

    if el.get("status") != "OK":
        return DriveTimeResult(status="error", error=el.get("status"))

    return DriveTimeResult(
        status="ok",
        distance_m=el.get("distance", {}).get("value"),
        duration_s=el.get("duration", {}).get("value"),
        duration_traffic_s=(el.get("duration_in_traffic") or {}).get("value"),
    )
