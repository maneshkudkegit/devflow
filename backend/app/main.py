"""
DevFlow – FastAPI application entry‑point.

Starts the ASGI server, registers routers, configures CORS,
and ensures the database tables exist on startup.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routes.slack import router as slack_router
from app.routes.api import router as api_router


# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("devflow")

# ── App ──
app = FastAPI(
    title="DevFlow – DevOps Automation Hub",
    description="Trigger deployments, manage users, and monitor activity from one API.",
    version="1.0.0",
)

# ── CORS (allow frontend dev server) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──
app.include_router(api_router)
app.include_router(slack_router)


# ── Startup ──
@app.on_event("startup")
def on_startup() -> None:
    """Create database tables if they don't exist yet."""
    logger.info("Creating database tables …")
    Base.metadata.create_all(bind=engine)
    logger.info("DevFlow backend is ready 🚀")


@app.get("/", tags=["health"])
def health_check() -> dict[str, str]:
    """Simple health/readiness probe."""
    return {"status": "ok", "service": "devflow-backend"}
