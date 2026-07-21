"""Provider-agnostic AI abstraction.

The rest of the app depends only on ``AIProvider`` so the concrete engine (currently
Ollama + Qwen3, always local and free) can be swapped without touching callers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AIProvider(ABC):
    """Abstract local LLM provider."""

    @abstractmethod
    def generate(self, prompt: str, *, system: str | None = None) -> str:
        """Return the model's plain-text completion for ``prompt``."""

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        schema: type[T],
        *,
        system: str | None = None,
        max_retries: int | None = None,
    ) -> T:
        """Return a validated instance of ``schema``.

        Forces JSON output, validates against the Pydantic ``schema``, and retries
        (feeding the error back to the model) on invalid JSON up to ``max_retries``.
        Raises ``InvalidJSONError`` if still invalid after retries.
        """

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for ``text`` (local embedding model)."""

    @abstractmethod
    def health(self) -> dict:
        """Return availability info: reachability, configured model, model presence."""
