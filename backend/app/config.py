import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "DocuForge AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security & Auth
    SECRET_KEY: str = "change-this-to-a-secure-random-secret-key-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Initial Admin Seed
    INITIAL_ADMIN_EMAIL: str = "admin@docuforge.ai"
    INITIAL_ADMIN_USERNAME: str = "admin"
    INITIAL_ADMIN_PASSWORD: str = "DocuForgeAdmin2026!"
    INITIAL_ADMIN_FULL_NAME: str = "System Administrator"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./docuforge_dev.db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "docuforge_user"
    POSTGRES_PASSWORD: str = "docuforge_secure_password"
    POSTGRES_DB: str = "docuforge_db"

    # Storage
    STORAGE_ROOT: str = "./storage"
    MAX_UPLOAD_SIZE_MB: int = 20

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # AI Provider
    AI_PROVIDER: str = "openai"
    AI_PROVIDER_API_KEY: str = ""
    AI_MODEL_NAME: str = "gpt-4o-mini"
    AI_REQUEST_TIMEOUT_SECONDS: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()

