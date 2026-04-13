"""
Global error handling middleware.
Catches unhandled exceptions and returns consistent JSON error envelopes.
"""
import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle FastAPI / Starlette HTTP exceptions."""
    logger.warning(
        f"HTTP {exc.status_code} | {request.method} {request.url} | {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "detail": None,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with clean field-level messages."""
    errors = []
    for err in exc.errors():
        field = " → ".join(str(loc) for loc in err["loc"])
        errors.append({"field": field, "message": err["msg"]})

    logger.warning(f"Validation error | {request.method} {request.url} | {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Request validation failed. Check the 'detail' field.",
            "detail": errors,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected server errors — never leak stack traces."""
    host = request.client.host if request.client else "unknown"
    logger.error(
        f"Unhandled exception | {request.method} {request.url} | Client: {host}\n"
        + traceback.format_exc()
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred. Please try again later.",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


def register_exception_handlers(app):
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
