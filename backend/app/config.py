"""Configuration: secrets come from backend/.env, everything else from config.yaml."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# repo root = .../Compeetah  (this file is backend/app/config.py)
REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Secrets and runtime knobs, loaded from backend/.env."""

    google_maps_api_key: str = ""
    owntracks_token: str = ""
    cors_origins: str = "*"
    database_url: str = "sqlite:///./data/compeetah.sqlite3"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[1] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# ---- config.yaml models -------------------------------------------------

class Place(BaseModel):
    label: str
    lat: float
    lon: float
    radius_m: float = 300.0
    address: str | None = None  # precise street address for maps/routing

    @property
    def waypoint(self) -> str:
        """Best string to hand Google for routing — address if we have one."""
        return self.address or f"{self.lat},{self.lon}"


class User(BaseModel):
    id: str
    name: str
    color: str = "#E50914"
    owntracks_tid: str = ""


class AppConfig(BaseModel):
    units: str = "imperial"
    poll_interval_minutes: int = 5
    drive_origin: str = "home"  # "home" | "live"
    home: Place
    work: Place
    users: list[User]

    def user(self, user_id: str) -> User | None:
        return next((u for u in self.users if u.id == user_id), None)


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_config() -> AppConfig:
    path = REPO_ROOT / "config.yaml"
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return AppConfig(**data)
