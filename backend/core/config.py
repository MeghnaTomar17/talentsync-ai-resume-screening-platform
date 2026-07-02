"""
Centralized FastAPI backend configuration.

Uses Pydantic settings when available and falls back to environment-backed
defaults in local environments that do not yet have pydantic-settings installed.
"""

from functools import lru_cache
from pathlib import Path

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # pragma: no cover - compatibility for current local venv
    import os

    from dotenv import dotenv_values
    from pydantic import BaseModel

    SettingsConfigDict = dict

    class BaseSettings(BaseModel):
        def __init__(self, **values):
            env_values = {
                **dotenv_values(".env"),
                **os.environ,
            }
            field_values = {}
            for field_name in self.model_fields:
                env_name = field_name.upper()
                if env_name in env_values:
                    field_values[field_name] = env_values[env_name]
            field_values.update(values)
            super().__init__(**field_values)


class Settings(BaseSettings):
    app_name: str = "TalentSync API"
    app_description: str = "AI-Powered Resume Screening and Career Intelligence Platform"
    app_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["*"]

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "all-MiniLM-L6-v2"

    faiss_index_dir: str = "faiss_index"
    jobs_dataset_path: str = "datasets/jobs.csv"
    upload_dir: str = "uploads"
    log_dir: str = "logs"
    log_file: str = "talentsync-api.log"
    log_max_bytes: int = 1_048_576
    log_backup_count: int = 5
    default_job_match_count: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def faiss_index_path(self) -> Path:
        return Path(self.faiss_index_dir)

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def jobs_path(self) -> Path:
        return Path(self.jobs_dataset_path)

    @property
    def log_path(self) -> Path:
        return Path(self.log_dir) / self.log_file


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
