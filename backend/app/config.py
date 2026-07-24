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

    # Local AI (Ollama + Qwen3). No paid APIs anywhere.
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"
    embedding_model: str = "nomic-embed-text"
    # Request timeout (seconds) for Ollama calls — local models can be slow to warm up.
    ollama_timeout: float = 120.0
    # Extra attempts when the model returns text that isn't valid JSON for the schema.
    ollama_json_max_retries: int = 2
    # Disable qwen3's <think> reasoning trace for cleaner, faster structured output.
    ollama_think: bool = False

    # Automation (Phase 11).
    auto_submit: bool = False

    # Where uploaded resume files are stored (relative to the backend working dir).
    upload_dir: str = "uploads"

    # Email (Phase 9). "mock" uses local fixtures; "gmail" requires OAuth creds.
    email_provider: str = "mock"
    gmail_credentials_file: str = "tokens/gmail_credentials.json"
    gmail_token_file: str = "tokens/gmail_token.json"
    # Below this confidence, an email classification is flagged NEEDS_REVIEW.
    email_classify_confidence_threshold: float = 0.6

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]


settings = Settings()
