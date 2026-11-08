"""Database connection and session factory using SQLAlchemy async engine."""

from __future__ import annotations

from pathlib import Path
from typing import AsyncGenerator

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

engine_kwargs = {"echo": settings.DEBUG, "future": True}
if "sqlite" in db_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


def _alembic_config() -> Config:
    config = Config(str(Path(__file__).resolve().parent / "../alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parent.parent / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    return config


async def create_db_and_tables() -> None:
    """Apply the Alembic migration chain instead of creating tables directly."""
    cfg = _alembic_config()
    try:
        command.upgrade(cfg, "head")
    except Exception:
        if "sqlite" not in settings.DATABASE_URL:
            raise
        async with engine.begin() as conn:
            existing_tables = await conn.run_sync(lambda sync_conn: list(sync_conn.execute(
                __import__("sqlalchemy", fromlist=["text"]).text("SELECT name FROM sqlite_master WHERE type='table'")
            )))
        if existing_tables:
            return
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for yielding an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
