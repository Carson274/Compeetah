"""Build the dashboard snapshot from the latest rows in the database, and
persist new readings."""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlencode

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import AppConfig, get_settings
from .models import (
    ChecklistItem,
    DriveTimeReading,
    LocationReading,
    SensorReading,
    WeatherReading,
)
from .providers.weather import describe
from .schemas import (
    ChecklistItemOut,
    CommuteOut,
    DashboardOut,
    PersonOut,
    PlaceOut,
    SensorOut,
    WeatherOut,
)


def _latest_weather(db: Session) -> WeatherOut | None:
    row = db.scalars(
        select(WeatherReading).order_by(WeatherReading.created_at.desc()).limit(1)
    ).first()
    if not row:
        return None
    return WeatherOut(
        temperature_c=row.temperature_c,
        apparent_c=row.apparent_c,
        humidity=row.humidity,
        wind_kmh=row.wind_kmh,
        weather_code=row.weather_code,
        is_day=row.is_day,
        description=describe(row.weather_code),
        as_of=row.created_at,
    )


def _latest_commute(db: Session, cfg: AppConfig) -> CommuteOut | None:
    row = db.scalars(
        select(DriveTimeReading).order_by(DriveTimeReading.created_at.desc()).limit(1)
    ).first()
    if not row:
        # no reading yet: distinguish "no API key" from "just haven't polled"
        status = "needs_key" if not get_settings().google_maps_api_key else "pending"
        return CommuteOut(
            origin_label=cfg.home.label, dest_label=cfg.work.label, status=status
        )
    return CommuteOut(
        origin_label=row.origin_label,
        dest_label=row.dest_label,
        distance_m=row.distance_m,
        duration_s=row.duration_s,
        duration_traffic_s=row.duration_traffic_s,
        as_of=row.created_at,
        status="ok" if row.duration_s is not None else "error",
    )


def _people(db: Session, cfg: AppConfig) -> list[PersonOut]:
    out: list[PersonOut] = []
    for u in cfg.users:
        row = db.scalars(
            select(LocationReading)
            .where(LocationReading.user == u.id)
            .order_by(LocationReading.recorded_at.desc())
            .limit(1)
        ).first()
        if not row:
            out.append(PersonOut(id=u.id, name=u.name, color=u.color, status="unknown"))
            continue
        out.append(
            PersonOut(
                id=u.id,
                name=u.name,
                color=u.color,
                is_home=row.is_home,
                place_label=cfg.home.label if row.is_home else None,
                distance_home_m=row.distance_home_m,
                lat=row.lat,
                lon=row.lon,
                battery=row.battery,
                velocity_kmh=row.velocity_kmh,
                last_seen=row.recorded_at,
                status="home" if row.is_home else "away",
            )
        )
    return out


def _sensors(db: Session) -> list[SensorOut]:
    # latest row per (sensor, metric), from the recent window
    rows = db.scalars(
        select(SensorReading).order_by(SensorReading.created_at.desc()).limit(500)
    ).all()
    seen: dict[tuple[str, str], SensorOut] = {}
    for r in rows:
        key = (r.sensor, r.metric)
        if key not in seen:
            seen[key] = SensorOut(
                sensor=r.sensor, metric=r.metric, value=r.value, unit=r.unit, as_of=r.created_at
            )
    return list(seen.values())


def _checklist(db: Session) -> list[ChecklistItemOut]:
    rows = db.scalars(
        select(ChecklistItem).order_by(ChecklistItem.position, ChecklistItem.id)
    ).all()
    return [
        ChecklistItemOut(
            id=r.id, text=r.text, done=r.done, position=r.position, assignee=r.assignee
        )
        for r in rows
    ]


def _map_embed_url(cfg: AppConfig) -> str | None:
    """Google Maps Embed (directions) URL for the home -> work route. Free,
    unlimited loads; needs the 'Maps Embed API' enabled on the same key."""
    key = get_settings().google_maps_api_key
    if not key:
        return None
    params = urlencode(
        {
            "key": key,
            "origin": cfg.home.waypoint,
            "destination": cfg.work.waypoint,
            "mode": "driving",
        }
    )
    return f"https://www.google.com/maps/embed/v1/directions?{params}"


def build_dashboard(db: Session, cfg: AppConfig) -> DashboardOut:
    commute = _latest_commute(db, cfg)
    commute.map_embed_url = _map_embed_url(cfg)
    return DashboardOut(
        units=cfg.units,
        home=PlaceOut(label=cfg.home.label, lat=cfg.home.lat, lon=cfg.home.lon),
        work=PlaceOut(label=cfg.work.label, lat=cfg.work.lat, lon=cfg.work.lon),
        weather=_latest_weather(db),
        commute=commute,
        people=_people(db, cfg),
        sensors=_sensors(db),
        checklist=_checklist(db),
        server_time=datetime.now(timezone.utc),
    )
