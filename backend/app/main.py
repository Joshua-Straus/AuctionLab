from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.database import SessionLocal
from backend.app.routes import router
from backend.app.seed import seed_experiments


@asynccontextmanager
async def lifespan(_: FastAPI):
    with SessionLocal() as session:
        seed_experiments(session)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Auction and Market Simulator API",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix="/api/v1")
    return application


app = create_app()
