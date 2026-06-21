"""Ingest endpoint for the OwnTracks phone app (HTTP mode).

Point the app at:  http(s)://<pi-host>:8000/api/owntracks?user=<your-id>
Set a password in the app == OWNTRACKS_TOKEN if you've set one in .env.
"""
from __future__ import annotations

import base64
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..config import AppConfig, Settings, get_config, get_settings
from ..db import get_session
from ..models import LocationReading, utcnow
from ..providers.location import OwnTracksProvider, geofence
from ..scheduler import broadcast_snapshot

router = APIRouter(prefix="/api/owntracks", tags=["owntracks"])
log = logging.getLogger("compeetah.owntracks")
_provider = OwnTracksProvider()


def _basic_auth(request: Request) -> tuple[str | None, str | None]:
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("basic "):
        return None, None
    try:
        user, _, pw = base64.b64decode(header[6:]).decode().partition(":")
        return user or None, pw or None
    except Exception:
        return None, None


def _check_token(request: Request, settings: Settings) -> None:
    if not settings.owntracks_token:
        return  # auth disabled (trusted LAN)
    _, pw = _basic_auth(request)
    supplied = (
        request.headers.get("x-owntracks-token")
        or request.query_params.get("token")
        or pw
    )
    if supplied != settings.owntracks_token:
        raise HTTPException(status_code=401, detail="bad owntracks token")


def _resolve_user(request: Request, payload: dict, cfg: AppConfig) -> str:
    basic_user, _ = _basic_auth(request)
    candidate = (
        request.query_params.get("user")
        or request.query_params.get("u")
        or request.headers.get("x-limit-u")
        or basic_user
    )
    if candidate and cfg.user(candidate):
        return candidate
    # fall back to matching the 2-char Tracker ID
    tid = payload.get("tid")
    if tid:
        match = next((u for u in cfg.users if u.owntracks_tid == tid), None)
        if match:
            return match.id
    return candidate or tid or "unknown"


@router.post("")
@router.post("/")
async def ingest(
    request: Request,
    db: Session = Depends(get_session),
    cfg: AppConfig = Depends(get_config),
    settings: Settings = Depends(get_settings),
):
    _check_token(request, settings)
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")

    fix = _provider.parse(payload)
    if fix is None:
        return []  # not a location message — OwnTracks expects a (possibly empty) array

    user_id = _resolve_user(request, payload, cfg)
    is_home, distance = geofence(fix, cfg.home)

    db.add(
        LocationReading(
            user=user_id,
            lat=fix.lat,
            lon=fix.lon,
            accuracy_m=fix.accuracy_m,
            battery=fix.battery,
            velocity_kmh=fix.velocity_kmh,
            altitude_m=fix.altitude_m,
            is_home=is_home,
            distance_home_m=distance,
            trigger=fix.trigger,
            source=fix.source,
            recorded_at=fix.recorded_at or utcnow(),
        )
    )
    db.commit()
    await broadcast_snapshot()
    return []
