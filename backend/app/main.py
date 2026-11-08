from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import admin, auth, departments, templates, users
from app.config import settings
from app.core.exceptions import AppException
from app.database import AsyncSessionLocal, create_db_and_tables
from app.db.seed import seed_default_admin, seed_system_roles
from app.models import *  # noqa: F401,F403


async def initialize_database() -> None:
    await create_db_and_tables()
    async with AsyncSessionLocal() as db:
        await seed_system_roles(db)
        await seed_default_admin(db)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await initialize_database()
    yield


try:
    asyncio.run(initialize_database())
except RuntimeError:
    # Runtime already has an event loop (e.g. tests or uvicorn), so the app
    # lifespan will initialize the database when the server starts.
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health")
async def api_health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/api/v1/ready")
async def api_ready() -> dict[str, str]:
    return {"status": "ready"}


app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(departments.router, prefix=settings.API_V1_STR)
app.include_router(templates.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code.value if hasattr(exc.code, 'value') else str(exc.code),
                "message": exc.message,
                "details": exc.details,
            }
        },
    )
