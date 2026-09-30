"""
DocuMind AI — Configuration & Core Infrastructure Tests
========================================================

Tests for Settings loading, Pydantic configuration, logging, exception handlers, and database utilities.
"""

import pytest
from app.core.config import Settings, get_settings
from app.core.database import check_database_connection
from app.core.exceptions import DocuMindException, EntityNotFoundException, ValidationException


def test_default_settings_values():
    """Verify default Settings values."""
    settings = Settings()
    assert settings.APP_NAME == "DocuMind AI"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.APP_ENV in ["development", "test", "production"]


def test_cors_origins_parsing():
    """Verify comma-separated origins are parsed into a list."""
    settings = Settings(ALLOWED_ORIGINS="http://localhost:3000, http://10.0.2.2:8000")
    origins = settings.cors_origins_list
    assert len(origins) == 2
    assert "http://localhost:3000" in origins
    assert "http://10.0.2.2:8000" in origins


def test_is_development_property():
    """Verify is_development property evaluation."""
    dev_settings = Settings(APP_ENV="development")
    prod_settings = Settings(APP_ENV="production")
    assert dev_settings.is_development is True
    assert prod_settings.is_development is False


def test_get_settings_lru_cache():
    """Verify get_settings returns cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_custom_exceptions():
    """Verify custom exception properties."""
    exc = EntityNotFoundException(entity_name="Document", entity_id="123")
    assert exc.status_code == 404
    assert "Document" in exc.message
    assert exc.details["entity_id"] == "123"

    val_exc = ValidationException(message="Invalid GSTIN")
    assert val_exc.status_code == 422
    assert val_exc.message == "Invalid GSTIN"


def test_check_database_connection_graceful():
    """Verify check_database_connection returns boolean without crashing if DB offline."""
    result = check_database_connection()
    assert isinstance(result, bool)
