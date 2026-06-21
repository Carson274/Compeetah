"""Time-series + state tables. Everything is append-only except checklist items,
so you can run statistics over history later."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LocationReading(Base):
    __tablename__ = "location_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column(String(64), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    battery: Mapped[int | None] = mapped_column(Integer, nullable=True)
    velocity_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_home: Mapped[bool] = mapped_column(Boolean, default=False)
    distance_home_m: Mapped[float] = mapped_column(Float, default=0.0)
    trigger: Mapped[str | None] = mapped_column(String(8), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="owntracks")
    # the moment the fix was taken (from the device), and when we stored it
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    temperature_c: Mapped[float] = mapped_column(Float)
    apparent_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    weather_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_day: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="open-meteo")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=utcnow)


class DriveTimeReading(Base):
    __tablename__ = "drivetime_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    origin_label: Mapped[str] = mapped_column(String(128))
    dest_label: Mapped[str] = mapped_column(String(128))
    distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_traffic_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="google")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=utcnow)


class SensorReading(Base):
    """Generic bucket for future Raspberry Pi sensors (temp, humidity, CO2, ...).
    One row per (sensor, metric) sample so new sensors need no schema change."""

    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    sensor: Mapped[str] = mapped_column(String(64), index=True)  # e.g. "living_room_bme280"
    metric: Mapped[str] = mapped_column(String(64), index=True)  # e.g. "temperature"
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=utcnow)


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(280))
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, default=0)
    assignee: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
