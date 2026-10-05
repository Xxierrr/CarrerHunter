"""
Internship Intelligence Platform — Application Configuration

Loads settings from environment variables with sensible defaults.
Uses pydantic-settings for validation and type coercion.
"""

import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Find .env file: check CWD first, then walk up to project root
def _find_env_file() -> str:
    """Find .env file by checking common locations."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent.parent.parent / ".env",  # project root
        Path(__file__).parent.parent / ".env",  # apps/api/.env
        Path(__file__).parent / ".env",  # apps/api/app/.env
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_env: str = "development"
    app_name: str = "Internship Intelligence"
    app_url: str = "http://localhost:3000"
    log_level: str = "INFO"

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./internship_intel.db"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Gemini AI ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_daily_limit: int = 1400
    gemini_rpm_limit: int = 14

    # --- Email ---
    email_provider: str = "resend"
    email_api_key: str = ""
    email_from: str = "Internship Intel <noreply@example.com>"
    email_daily_limit: int = 100

    # --- JWT Auth ---
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION_TO_A_RANDOM_SECRET"
    jwt_algorithm: str = "HS256"
    jwt_access_expiry_minutes: int = 15
    jwt_refresh_expiry_days: int = 7

    # --- Frontend ---
    frontend_url: str = "http://localhost:3000"
    next_public_api_url: str = "http://localhost:8000"

    # --- Monitoring ---
    sentry_dsn: str = ""

    # --- File Uploads ---
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance. Call this instead of creating Settings() directly."""
    return Settings()
