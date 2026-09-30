"""
DocuMind AI — Database Infrastructure
====================================

SQLAlchemy engine, session factory, base model declarative class,
and database connection health checks.
"""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
from app.core.logging import logger

# Create SQLAlchemy Engine
# Note: pool_pre_ping=True tests connections before handing them out
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG and settings.is_development,
    connect_args={"connect_timeout": 2},
)

# Session factory for DB interactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


def get_db() -> Generator:
    """
    FastAPI dependency that yields a database session per request.
    Ensures connection is closed when request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """
    Check if the database connection is healthy.
    Returns True if reachable, False otherwise (without raising unhandled exceptions).
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")
        return False
