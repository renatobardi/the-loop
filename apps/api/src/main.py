"""FastAPI app factory for The Loop incident API."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.firebase.auth import init_firebase
from src.api.middleware import setup_middleware
from src.api.routes.action_items import router as action_items_router
from src.api.routes.analytics import router as analytics_router
from src.api.routes.api_keys import router as api_keys_router
from src.api.routes.attachments import router as attachments_router
from src.api.routes.incidents import router as incidents_router
from src.api.routes.postmortems import router as postmortems_router
from src.api.routes.releases import router as releases_router
from src.api.routes.releases_admin import router as releases_admin_router
from src.api.routes.responders import router as responders_router
from src.api.routes.rules import router as rules_router
from src.api.routes.scans import router as scans_router
from src.api.routes.timeline import router as timeline_router
from src.api.routes.users import router as users_router
from src.config import settings

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
        if settings.log_level == "DEBUG"
        else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(settings.log_level)),
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_firebase()
    yield


app = FastAPI(
    title="The Loop — Incident API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

setup_middleware(app)
app.include_router(incidents_router)
app.include_router(analytics_router)
app.include_router(timeline_router)
app.include_router(responders_router)
app.include_router(action_items_router)
app.include_router(attachments_router)
app.include_router(postmortems_router)
app.include_router(releases_router)
app.include_router(releases_admin_router)
app.include_router(rules_router)
app.include_router(users_router)
app.include_router(api_keys_router)
app.include_router(scans_router)


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
