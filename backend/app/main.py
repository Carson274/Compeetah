"""Compeetah API + websocket server."""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select

from .config import REPO_ROOT, get_settings
from .db import SessionLocal, init_db
from .models import ChecklistItem
from .routers import checklist, dashboard, owntracks, sensors
from .scheduler import poll_once, start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("compeetah")

DEFAULT_CHECKLIST = [
    "Set up OwnTracks on both phones",
    "Add the Google Maps API key to backend/.env",
    "Water the plants",
    "Take out the trash",
]


def seed_checklist() -> None:
    with SessionLocal() as db:
        if db.scalar(select(func.count(ChecklistItem.id))) == 0:
            for i, text in enumerate(DEFAULT_CHECKLIST, start=1):
                db.add(ChecklistItem(text=text, position=i))
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_checklist()
    start_scheduler()
    asyncio.create_task(poll_once())  # populate weather/commute immediately
    log.info("Compeetah backend ready")
    try:
        yield
    finally:
        stop_scheduler()


app = FastAPI(title="Compeetah", version="0.1.0", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(owntracks.router)
app.include_router(checklist.router)
app.include_router(sensors.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# In production the Pi serves the built React app from here too (single port).
# In dev you'll use the Vite server instead, which proxies /api and /ws back.
# The catch-all is an SPA fallback so client routes like /control return index.html.
_dist = REPO_ROOT / "frontend" / "dist"
if _dist.exists():
    app.mount("/assets", StaticFiles(directory=str(_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        candidate = _dist / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_dist / "index.html")
