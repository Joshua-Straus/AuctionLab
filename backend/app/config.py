from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    cors_origins: tuple[str, ...]


def get_settings() -> Settings:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:8501")
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://auction:auction@localhost:5432/auction_simulator",
        ),
        cors_origins=tuple(origin.strip() for origin in origins.split(",") if origin.strip()),
    )
