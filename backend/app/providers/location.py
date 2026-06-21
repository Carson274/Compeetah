"""Location layer.

Today this ingests OwnTracks HTTP pushes. The `LocationProvider` base class
marks the seam where a different source (Mac Find My bridge, FindMy.py, a GPS
sensor) could be dropped in without touching the rest of the app.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

from ..config import Place
from ..geo import haversine_m


@dataclass
class Fix:
    """A normalized location fix, source-agnostic."""

    lat: float
    lon: float
    accuracy_m: float | None = None
    battery: int | None = None
    velocity_kmh: float | None = None
    altitude_m: float | None = None
    trigger: str | None = None
    recorded_at: datetime | None = None
    source: str = "owntracks"


class LocationProvider(ABC):
    name: str = "base"

    @abstractmethod
    def parse(self, payload: dict) -> Fix | None:
        """Turn a raw provider payload into a Fix, or None to ignore it."""


class OwnTracksProvider(LocationProvider):
    name = "owntracks"

    def parse(self, payload: dict) -> Fix | None:
        # OwnTracks sends several message types; we only persist location fixes.
        if payload.get("_type") != "location":
            return None
        lat, lon = payload.get("lat"), payload.get("lon")
        if lat is None or lon is None:
            return None

        ts = payload.get("tst")
        recorded = (
            datetime.fromtimestamp(ts, tz=timezone.utc) if isinstance(ts, (int, float)) else None
        )
        vel = payload.get("vel")  # OwnTracks velocity is km/h already

        return Fix(
            lat=float(lat),
            lon=float(lon),
            accuracy_m=payload.get("acc"),
            battery=payload.get("batt"),
            velocity_kmh=float(vel) if isinstance(vel, (int, float)) else None,
            altitude_m=payload.get("alt"),
            trigger=payload.get("t"),  # p=ping, u=manual, c=region, etc.
            recorded_at=recorded,
            source="owntracks",
        )


def geofence(fix: Fix, home: Place) -> tuple[bool, float]:
    """Return (is_home, distance_from_home_m)."""
    dist = haversine_m(fix.lat, fix.lon, home.lat, home.lon)
    return dist <= home.radius_m, dist
