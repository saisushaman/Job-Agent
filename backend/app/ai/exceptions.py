"""AI layer exceptions."""

from __future__ import annotations


class AIProviderError(RuntimeError):
    """Base error for AI provider failures (connectivity, bad status, etc.)."""


class AIUnavailableError(AIProviderError):
    """The AI backend (Ollama) could not be reached."""


class InvalidJSONError(AIProviderError):
    """The model failed to return JSON matching the requested schema after retries."""
