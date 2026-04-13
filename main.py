"""
OrgoLife — Organ Donation Platform
Master FastAPI Entry Point with full CORS, routes, and middleware.
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.database import connect_db, close_db
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.api.routes import admin, receiver
from app.api.routes import auth as auth_router
from app.api.routes import donor as donor_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 OrgoLife backend starting up...")
    await connect_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("\n" + "="*50 + "\n🚀 ORGOLIFE IS READY!\nAccess the portal at: http://localhost:8000\n" + "="*50 + "\n")
    yield
    logger.info("🛑 OrgoLife backend shutting down...")
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Organ Donation Platform — connecting donors, receivers, and hospitals.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────
# Allows frontend (same origin or opened as file/dev server) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request logging ───────────────────────────────────────────────
app.add_middleware(RequestLoggingMiddleware)

# ── Uploaded document files ───────────────────────────────────────
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Register global error handlers ───────────────────────────────
register_exception_handlers(app)

# ── API routes ────────────────────────────────────────────────────
PREFIX = settings.API_V1_PREFIX  # "/api/v1"

app.include_router(auth_router.router,  prefix=PREFIX)
app.include_router(donor_router.router, prefix=PREFIX)
app.include_router(receiver.router,     prefix=PREFIX)
app.include_router(admin.router,        prefix=PREFIX)

# ── Health check ──────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# ── Serve frontend ────────────────────────────────────────────────
# Mount static assets from frontend/ directory (CSS, JS, images if any)
# then fall back to index.html for the root route.
if os.path.isdir(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

    @app.get("/", tags=["Frontend"])
    async def serve_frontend():
        """Serve the single-page frontend application."""
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    @app.get("/", tags=["System"])
    async def root():
        return {
            "message": "OrgoLife Organ Donation Platform API",
            "docs": "/api/docs",
            "version": settings.APP_VERSION,
        }
