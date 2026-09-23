from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CA Student OS API"
    app_env: str = "development"
    database_url: str = "sqlite+aiosqlite:///./data/studentos-dev.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "development-only-change-this-secret-key-please"
    jwt_issuer: str = "ca-student-os"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]
    storage_driver: Literal["local", "s3"] = "local"
    local_storage_path: str = "data/uploads"
    s3_endpoint_url: str | None = None
    s3_bucket: str | None = None
    s3_region: str = "auto"
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    upload_max_bytes: int = 15 * 1024 * 1024

    # CORS_ORIGINS is intentionally accepted as a comma-separated environment
    # variable (for example, "http://localhost:3000,https://app.example.com").
    # Disable pydantic-settings' automatic JSON decoding so the validator below
    # can normalize that deployment-friendly format before validation.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        enable_decoding=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        if self.app_env == "production" and self.jwt_secret_key.startswith("development-only"):
            raise ValueError("JWT_SECRET_KEY must be replaced in production")
        if self.storage_driver == "s3" and not self.s3_bucket:
            raise ValueError("S3_BUCKET is required when STORAGE_DRIVER=s3")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
