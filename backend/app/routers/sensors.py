"""Intake for future Raspberry Pi sensors.

A little script on the Pi (reading a BME280, DHT22, etc.) can POST here:

    POST /api/sensors
    {"sensor": "living_room_bme280", "metric": "temperature", "value": 22.4, "unit": "C"}

or a batch:  {"readings": [ {...}, {...} ]}
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import SensorReading
from ..scheduler import broadcast_snapshot

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


class SensorIn(BaseModel):
    sensor: str
    metric: str
    value: float
    unit: str | None = None


class SensorBatch(BaseModel):
    readings: list[SensorIn]


@router.post("", status_code=201)
async def ingest(body: SensorIn | SensorBatch, db: Session = Depends(get_session)):
    items = body.readings if isinstance(body, SensorBatch) else [body]
    for r in items:
        db.add(SensorReading(sensor=r.sensor, metric=r.metric, value=r.value, unit=r.unit))
    db.commit()
    await broadcast_snapshot()
    return {"stored": len(items)}
