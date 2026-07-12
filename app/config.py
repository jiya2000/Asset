"""
Application configuration — loaded from environment variables.
All secrets and connection strings live here; nothing is hard-coded.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/assetflow"

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "super-secret-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── App ───────────────────────────────────────────────────
    APP_NAME: str = "AssetFlow"
    DEBUG: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
