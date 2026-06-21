"""Background polling: every N minutes refresh weather + drive time, store a
row for history, and push the new snapshot to connected screens."""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import AppConfig, Settings, get_config, get_settings
from .db import SessionLocal
from .models import DriveTimeReading, LocationReading, WeatherReading
from .providers.drivetime import fetch_drive_time
from .providers.weather import fetch_weather
from .services import build_dashboard
from .ws import hub

log = logging.getLogger("compeetah.scheduler")
_scheduler: AsyncIOScheduler | None = None


def _drive_origin(db, cfg: AppConfig) -> tuple[float, float, str]:
    """Resolve where the commute is measured from."""
    if cfg.drive_origin == "live":
        from sqlalchemy import select

        row = db.scalars(
            select(LocationReading).order_by(LocationReading.recorded_at.desc()).limit(1)
        ).first()
        if row:
            return row.lat, row.lon, "Current location"
    return cfg.home.lat, cfg.home.lon, cfg.home.label


async def refresh_weather(cfg: AppConfig) -> None:
    try:
        data = await fetch_weather(cfg.home.lat, cfg.home.lon)
    except Exception as exc:
        log.warning("weather fetch failed: %s", exc)
        return
    if data.get("temperature_c") is None:
        return
    with SessionLocal() as db:
        db.add(WeatherReading(lat=cfg.home.lat, lon=cfg.home.lon, **data))
        db.commit()


async def refresh_drive_time(cfg: AppConfig, settings: Settings) -> None:
    with SessionLocal() as db:
        olat, olon, olabel = _drive_origin(db, cfg)
    result = await fetch_drive_time(
        olat, olon, cfg.work.lat, cfg.work.lon, settings.google_maps_api_key
    )
    if result.get("status") != "ok":
        if result.get("status") != "needs_key":
            log.warning("drive time: %s", result.get("error") or result.get("status"))
        return
    with SessionLocal() as db:
        db.add(
            DriveTimeReading(
                origin_label=olabel,
                dest_label=cfg.work.label,
                distance_m=result.get("distance_m"),
                duration_s=result.get("duration_s"),
                duration_traffic_s=result.get("duration_traffic_s"),
            )
        )
        db.commit()


async def poll_once() -> None:
    cfg, settings = get_config(), get_settings()
    await refresh_weather(cfg)
    await refresh_drive_time(cfg, settings)
    await broadcast_snapshot()


async def broadcast_snapshot() -> None:
    cfg = get_config()
    with SessionLocal() as db:
        snapshot = build_dashboard(db, cfg)
    await hub.broadcast({"type": "dashboard", "data": snapshot.model_dump(mode="json")})


def start_scheduler() -> AsyncIOScheduler:
    global _scheduler
    cfg = get_config()
    _scheduler = AsyncIOScheduler(timezone="UTC")
    _scheduler.add_job(
        poll_once,
        "interval",
        minutes=max(1, cfg.poll_interval_minutes),
        id="poll",
        next_run_time=None,
    )
    _scheduler.start()
    return _scheduler


def stop_scheduler() -> None:
    if _scheduler:
        _scheduler.shutdown(wait=False)
