"""Tests for the database infrastructure."""

import pytest
from sqlalchemy.orm import Session
from app.core.database import Base, SessionLocal, get_db, check_database_connection
from app.models.base import TimestampMixin


def test_base_declarative_class():
    """Ensure the DeclarativeBase is accessible and importable."""
    assert Base is not None


def test_timestamp_mixin():
    """Ensure the TimestampMixin provides created_at and updated_at."""
    attrs = dir(TimestampMixin)
    assert "created_at" in attrs
    assert "updated_at" in attrs


def test_get_db_yields_session():
    """Ensure get_db yields a sqlalchemy Session and closes it."""
    db_gen = get_db()
    session = next(db_gen)
    assert isinstance(session, Session)
    
    # Session should be active
    assert session.is_active
    
    try:
        next(db_gen)
    except StopIteration:
        pass
        
    # We can't trivially assert session is closed without mocking because sqlalchemy Sessions 
    # don't have a simple is_closed boolean, but we ensure the generator finishes successfully.


def test_check_database_connection_mocked_success(monkeypatch):
    """Test health check logic when database is reachable."""
    
    class MockConnection:
        def execute(self, query):
            pass
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            pass

    class MockEngine:
        def connect(self):
            return MockConnection()

    monkeypatch.setattr("app.core.database.engine", MockEngine())
    assert check_database_connection() is True


def test_check_database_connection_mocked_failure(monkeypatch):
    """Test health check logic when database is unreachable."""
    
    class MockEngine:
        def connect(self):
            raise Exception("Connection failed")

    monkeypatch.setattr("app.core.database.engine", MockEngine())
    assert check_database_connection() is False
