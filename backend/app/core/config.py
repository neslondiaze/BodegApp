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

    # JWT RS256 key material (loaded from file paths, never hardcoded)
    jwt_private_key_path: str = "secrets/jwt_private_key.pem"
    jwt_public_key_path: str = "secrets/jwt_public_key.pem"

    # Token lifetimes — contract §1: work token short, contractor token long
    access_token_minutes: int = 15
    refresh_token_days: int = 7

    # Clock skew tolerance for JWT verification (seconds) — QA B4
    jwt_clock_leeway_seconds: int = 30

    # Refresh rotation (contract rule T3), enabled by default (QA-ST02-01):
    # each refresh issues a new contractor token and reuse of a rotated one
    # revokes the whole chain. The frontend persists the rotated token since
    # QA-F04-03 (apiClient.ts:83-86 stores it atomically with the new access
    # token). The flag remains as an operational kill-switch.
    refresh_rotation_enabled: bool = True

    # CORS — only declared frontend origins, never "*" (integration contract §3.4)
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
