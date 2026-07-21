"""Provider wiring. The rest of the app depends on ``get_ai_provider``."""

from __future__ import annotations

from functools import lru_cache

from app.ai.base import AIProvider
from app.ai.providers import OllamaProvider
from app.config import settings


@lru_cache
def get_ai_provider() -> AIProvider:
    """Return the configured (local) AI provider — currently Ollama + Qwen3."""
    return OllamaProvider(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        embedding_model=settings.embedding_model,
        timeout=settings.ollama_timeout,
        max_retries=settings.ollama_json_max_retries,
        think=settings.ollama_think,
    )
