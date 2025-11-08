"""Database connection and session management."""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config import settings
from src.database.models import Base
from src.utils import get_logger

logger = get_logger()

# Create async engine
engine = None
async_session_maker = None


def get_database_url() -> str:
    """Get database URL from environment variables.
    
    Returns:
        Database URL string
    """
    # Vercel provides POSTGRES_URL for Neon
    db_url = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
    
    if not db_url:
        raise ValueError(
            "Database URL not found. Set POSTGRES_URL or DATABASE_URL environment variable."
        )
    
    # Convert postgres:// to postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return db_url


def init_db():
    """Initialize database engine and session maker."""
    global engine, async_session_maker
    
    if engine is not None:
        return
    
    try:
        db_url = get_database_url()
        
        engine = create_async_engine(
            db_url,
            echo=settings.LOG_LEVEL == "DEBUG",
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        logger.info("Database connection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def create_tables():
    """Create all database tables."""
    if engine is None:
        init_db()
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


async def drop_tables():
    """Drop all database tables. Use with caution!"""
    if engine is None:
        init_db()
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session.
    
    Usage:
        async with get_db_session() as session:
            result = await session.execute(query)
    
    Yields:
        AsyncSession instance
    """
    if async_session_maker is None:
        init_db()
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db():
    """Close database connections."""
    global engine, async_session_maker
    
    if engine is not None:
        await engine.dispose()
        engine = None
        async_session_maker = None
        logger.info("Database connections closed")
