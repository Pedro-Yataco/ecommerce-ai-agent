from collections.abc import AsyncGenerator
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class DatabaseSettings(BaseSettings):
    """Database configuration loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://ecommerce:ecommerce@localhost:5432/ecommerce"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """Return cached database settings."""
    return DatabaseSettings()


def create_database_engine() -> AsyncEngine:
    """Create the async SQLAlchemy engine."""
    settings = get_database_settings()

    return create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )


engine: AsyncEngine = create_database_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async with AsyncSessionLocal() as session:
        yield session