from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables (BODEGAPP_ prefix)."""

    model_config = SettingsConfigDict(
        env_prefix="BODEGAPP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "BodegApp API"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./bodegapp.db"

    # JWT RS256 key material (F0-04 will build full auth on top of this)
    jwt_private_key_path: str = "secrets/jwt_private_key.pem"
    jwt_public_key_path: str = "secrets/jwt_public_key.pem"

    # Token lifetimes (seconds) — contract: INTEGRACION-BACKEND-FRONTEND.md §1
    access_token_minutes: int = 15
    refresh_token_days: int = 7

    # CORS — only declared frontend origins, never "*" (integration contract §3.4)
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
