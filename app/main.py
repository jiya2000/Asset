"""
AssetFlow — Enterprise Asset Management System
FastAPI application entry point.

Registers all routers, configures CORS, and exposes health check.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, assets, allocations, maintenance, dashboard

settings = get_settings()

app = FastAPI(
    title="AssetFlow API",
    description="Enterprise Asset Management System — track, allocate, maintain, and transfer organizational assets with full audit trail.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Router registration ──────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(allocations.router)
app.include_router(maintenance.router)
app.include_router(dashboard.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
