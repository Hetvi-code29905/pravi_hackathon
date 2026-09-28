"""
Main FastAPI Application Entrypoint.
Initializes lifespan (Beanie + MongoDB), CORS middleware, and includes all routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db
from app.auth.routes import router as auth_router
from app.routes.infrastructure import router as infra_router
from app.routes.projects import router as projects_router
from app.routes.assets import router as assets_router
from app.routes.operations import router as operations_router
from app.routes.dashboard import router as dashboard_router
from app.seed import seed_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB and Beanie ODM
    await init_db()
    yield
    # Shutdown: Close database connection
    await close_db()


app = FastAPI(
    title="Gujarat R&B Infrastructure Lifecycle & Asset Management Platform",
    description="Enterprise lifecycle state machine, Asset Passport, condition monitoring, risk scoring, and intervention engine.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all during development and hackathon evaluation
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(infra_router)
app.include_router(projects_router)
app.include_router(assets_router)
app.include_router(operations_router)
app.include_router(dashboard_router)
app.include_router(seed_router)


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Gujarat R&B Infrastructure Lifecycle Engine",
        "version": "1.0.0",
        "database": settings.DATABASE_NAME,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
