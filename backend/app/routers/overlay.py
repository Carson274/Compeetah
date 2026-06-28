"""Toggle the full-screen overlay shown on the TV (controlled from a phone)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..scheduler import broadcast_snapshot
from ..state import OVERLAYS, state

router = APIRouter(prefix="/api/overlay", tags=["overlay"])


class OverlayIn(BaseModel):
    overlay: str | None = None  # an allowed overlay name, or null to clear


@router.get("")
def get_overlay():
    return {"overlay": state.overlay}


@router.post("")
async def set_overlay(body: OverlayIn):
    if body.overlay is not None and body.overlay not in OVERLAYS:
        raise HTTPException(status_code=422, detail=f"unknown overlay: {body.overlay}")
    state.overlay = body.overlay
    await broadcast_snapshot()
    return {"overlay": state.overlay}
