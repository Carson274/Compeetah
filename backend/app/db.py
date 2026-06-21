"""SQLite engine + session helpers."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import REPO_ROOT, get_settings

settings = get_settings()

# Resolve a sqlite:///./relative path against the repo root and make sure the
# parent directory exists, so a fresh checkout "just works".
url = settings.database_url
if url.startswith("sqlite:///./"):
    db_path = (REPO_ROOT / url.replace("sqlite:///./", "", 1)).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{db_path}"

engine = create_engine(
    url,
    echo=False,
    connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401  (register tables)

    Base.metadata.create_all(engine)
