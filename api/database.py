"""
Database Configuration and Session Management
PostgreSQL database setup with SQLAlchemy
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

try:
    from api.config import settings
except ImportError:
    from config import settings

# Database URL
# Default to SQLite for ease of use without Docker/Postgres
DEFAULT_SQLITE_URL = "sqlite+aiosqlite:///./data_cleaning.db"
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Check if we should use PostgreSQL or SQLite as default
    # If DB_HOST is localhost and we can't connect, SQLite is a safer default for "just working"
    DATABASE_URL = DEFAULT_SQLITE_URL
    print(f"ℹ️  No DATABASE_URL found. Using SQLite: {DATABASE_URL}")

# Sync database URL for Alembic migrations
if "sqlite" in DATABASE_URL:
    SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")
else:
    SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "").replace("asyncpg://", "psycopg2://")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


# Dependency to get database session
async def get_db() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Sync engine for migrations
sync_engine = create_engine(SYNC_DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()

