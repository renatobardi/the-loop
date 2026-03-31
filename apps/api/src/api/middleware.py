"""Middleware: rate limiting, request ID, structured logging."""

from __future__ import annotations

import uuid

import structlog
from fastapi import FastAPI, Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import settings

logger = structlog.get_logger()


def _get_user_key(request: Request) -> str:
    """Extract rate-limit key from authenticated user or fall back to IP."""
    if hasattr(request.state, "user_id"):
        return str(request.state.user_id)
    return get_remote_address(request)


limiter = Limiter(key_func=_get_user_key, default_limits=[settings.rate_limit])


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    retry_after = getattr(exc, "retry_after", 60)
    return Response(
        content=f'{{"detail":"Rate limit exceeded. Retry after {retry_after}s"}}',
        status_code=429,
        media_type="application/json",
        headers={"Retry-After": str(retry_after)},
    )


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        return response


def setup_middleware(app: FastAPI) -> None:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_middleware(RequestIdMiddleware)
