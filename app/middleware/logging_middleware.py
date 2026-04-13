"""
Request / response logging middleware.
Logs method, path, status code, and response time for every request.
"""
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("organ_donation.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()

        # ── Log incoming request ──────────────────────────────────
        logger.info(
            f"→ {request.method} {request.url.path} "
            f"| IP: {request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Unhandled in middleware: {exc}")
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000

        # ── Log outgoing response ─────────────────────────────────
        logger.info(
            f"← {request.method} {request.url.path} "
            f"| status={response.status_code} | {elapsed_ms:.1f}ms"
        )

        # Expose timing header for debugging
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
        return response
