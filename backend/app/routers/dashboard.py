"""Read API + websocket the screens subscribe to."""
from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ..config import AppConfig, get_config
from ..db import SessionLocal, get_session
from ..schemas import DashboardOut
from ..services import build_dashboard
from ..ws import hub

router = APIRouter(tags=["dashboard"])


@router.get("/api/dashboard", response_model=DashboardOut)
def get_dashboard(
    db: Session = Depends(get_session),
    cfg: AppConfig = Depends(get_config),
) -> DashboardOut:
    return build_dashboard(db, cfg)


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await hub.connect(ws)
    try:
        # push a snapshot immediately so a freshly-loaded screen isn't blank
        cfg = get_config()
        with SessionLocal() as db:
            snapshot = build_dashboard(db, cfg)
        await ws.send_json({"type": "dashboard", "data": snapshot.model_dump(mode="json")})
        while True:
            await ws.receive_text()  # we don't expect client messages; keeps the socket open
    except WebSocketDisconnect:
        pass
    finally:
        await hub.disconnect(ws)
