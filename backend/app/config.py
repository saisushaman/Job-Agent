"""Application settings, loaded from environment / .env (Pydantic Settings)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Job-Agent API"
    app_version: str = "0.1.0"
    environment: str = "development"

    # Database — SQLite by default so Phase 1 runs with no extra services.
    database_url: str = "sqlite:///./job_agent.db"

    # CORS: comma-separated list of allowed frontend origins.
    backend_cors_origins: str = "http://localhost:3000"

    # Local AI (Phase 2+, unused in Phase 1 but read here so config stays central).
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"
    embedding_model: str = "nomic-embed-text"

    # Automation (Phase 11).
    auto_submit: bool = False

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]


settings = Settings()
