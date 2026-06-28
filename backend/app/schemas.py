"""Pydantic response shapes returned by the API / pushed over the websocket."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PlaceOut(BaseModel):
    label: str
    lat: float
    lon: float


class WeatherOut(BaseModel):
    temperature_c: float
    apparent_c: float | None = None
    humidity: float | None = None
    wind_kmh: float | None = None
    weather_code: int | None = None
    is_day: bool | None = None
    description: str = ""
    as_of: datetime | None = None


class CommuteOut(BaseModel):
    origin_label: str
    dest_label: str
    distance_m: float | None = None
    duration_s: float | None = None
    duration_traffic_s: float | None = None
    as_of: datetime | None = None
    status: str = "ok"  # ok | needs_key | error | pending
    map_embed_url: str | None = None  # Google Maps Embed (directions) iframe src


class PersonOut(BaseModel):
    id: str
    name: str
    color: str
    is_home: bool | None = None
    place_label: str | None = None
    distance_home_m: float | None = None
    lat: float | None = None
    lon: float | None = None
    battery: int | None = None
    velocity_kmh: float | None = None
    last_seen: datetime | None = None
    status: str = "unknown"  # home | away | unknown


class SensorOut(BaseModel):
    sensor: str
    metric: str
    value: float
    unit: str | None = None
    as_of: datetime


class ChecklistItemOut(BaseModel):
    id: int
    text: str
    done: bool
    position: int
    assignee: str | None = None


class ChecklistItemIn(BaseModel):
    text: str
    assignee: str | None = None


class ChecklistItemPatch(BaseModel):
    text: str | None = None
    done: bool | None = None
    position: int | None = None
    assignee: str | None = None


class DashboardOut(BaseModel):
    units: str
    overlay: str | None = None  # full-screen TV overlay, e.g. "secret_hitler"
    home: PlaceOut
    work: PlaceOut
    weather: WeatherOut | None = None
    commute: CommuteOut | None = None
    people: list[PersonOut] = []
    sensors: list[SensorOut] = []
    checklist: list[ChecklistItemOut] = []
    server_time: datetime
