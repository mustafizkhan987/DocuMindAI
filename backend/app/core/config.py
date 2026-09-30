"""
DocuMind AI — Application Configuration
========================================

Centralized configuration using Pydantic Settings.
Environment variables can override default values.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings schema and defaults."""

    APP_NAME: str = "DocuMind AI"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-32-chars-min"

    # Database
    DATABASE_URL: str = "postgresql+psycopg://documind:documind@localhost:5432/documind"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://10.0.2.2:8000,http://localhost:8000"

    # Storage
    MAX_UPLOAD_SIZE_MB: int = 10
    STORAGE_DIR: str = "storage/documents"
    PROCESSED_DIR: str = "storage/processed"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated ALLOWED_ORIGINS string into a list of strings."""
        if not self.ALLOWED_ORIGINS:
            return ["http://localhost:8000"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        """Return True if running in development mode."""
        return self.APP_ENV.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """FastAPI dependency or utility to get cached Settings instance."""
    return Settings()


settings = get_settings()
