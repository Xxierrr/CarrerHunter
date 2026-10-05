"""
Internship Intelligence Platform — Database Configuration

Async SQLAlchemy engine and session factory.
Supports both PostgreSQL (production) and SQLite (local dev).
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# Determine engine options based on database type
engine_kwargs = {
    "echo": settings.is_development,
}

# SQLite doesn't support pool_pre_ping, pool_size, or max_overflow the same way
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

# Create async engine
engine = create_async_engine(
    settings.database_url,
    **engine_kwargs,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables. Used for development/testing only."""
    # Import all models so Base.metadata knows about them
    import app.models.user  # noqa: F401
    import app.models.profile  # noqa: F401
    import app.models.internship  # noqa: F401
    import app.models.application  # noqa: F401
    import app.models.notification  # noqa: F401
    import app.models.system  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
