"""Ollama-backed AI provider (local Qwen3). No paid APIs.

Talks to the Ollama REST API:
- POST /api/chat        — chat completion
- POST /api/embeddings  — embedding vector
- GET  /api/tags        — installed models (used for health)
"""

from __future__ import annotations

import json
import re
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.ai.base import AIProvider
from app.ai.exceptions import AIUnavailableError, InvalidJSONError

T = TypeVar("T", bound=BaseModel)

# qwen3 may wrap reasoning in <think>...</think>; strip it defensively.
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_think(text: str) -> str:
    return _THINK_RE.sub("", text).strip()


class OllamaProvider(AIProvider):
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        embedding_model: str,
        timeout: float = 120.0,
        max_retries: int = 2,
        think: bool = False,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.embedding_model = embedding_model
        self.max_retries = max_retries
        self.think = think
        self._client = client or httpx.Client(base_url=self.base_url, timeout=timeout)

    # -- low-level ---------------------------------------------------------

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            resp = self._client.post(path, json=payload)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:  # non-2xx from Ollama
            raise AIUnavailableError(
                f"Ollama returned {exc.response.status_code} for {path}"
            ) from exc
        except httpx.HTTPError as exc:  # connection/timeout errors
            raise AIUnavailableError(f"Could not reach Ollama at {self.base_url}") from exc
        return resp.json()

    def _chat(self, prompt: str, system: str | None, *, as_json: bool) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": self.think,
        }
        if as_json:
            payload["format"] = "json"

        data = self._post("/api/chat", payload)
        content = (data.get("message") or {}).get("content", "")
        return _strip_think(content)

    # -- AIProvider --------------------------------------------------------

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        return self._chat(prompt, system, as_json=False)

    def generate_json(
        self,
        prompt: str,
        schema: type[T],
        *,
        system: str | None = None,
        max_retries: int | None = None,
    ) -> T:
        retries = self.max_retries if max_retries is None else max_retries
        schema_json = json.dumps(schema.model_json_schema())
        base_instruction = (
            f"{prompt}\n\n"
            "Respond with ONLY a single valid JSON object matching this JSON schema. "
            "Do not include markdown fences, comments, or any prose.\n"
            f"JSON schema:\n{schema_json}"
        )

        current = base_instruction
        last_error: Exception | None = None

        for _ in range(retries + 1):
            raw = self._chat(current, system, as_json=True)
            try:
                parsed = json.loads(raw)
                return schema.model_validate(parsed)
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
                current = (
                    f"{base_instruction}\n\n"
                    f"Your previous answer was invalid ({exc}). "
                    "Return corrected JSON only."
                )

        raise InvalidJSONError(
            f"Model did not produce valid JSON for {schema.__name__} "
            f"after {retries + 1} attempts"
        ) from last_error

    def embed(self, text: str) -> list[float]:
        data = self._post(
            "/api/embeddings", {"model": self.embedding_model, "prompt": text}
        )
        return data.get("embedding", [])

    def health(self) -> dict:
        try:
            resp = self._client.get("/api/tags")
            resp.raise_for_status()
        except httpx.HTTPError:
            return {
                "available": False,
                "base_url": self.base_url,
                "model": self.model,
                "model_available": False,
                "models": [],
            }

        names = [m.get("name", "") for m in resp.json().get("models", [])]
        return {
            "available": True,
            "base_url": self.base_url,
            "model": self.model,
            "model_available": self.model in names,
            "models": names,
        }

    def close(self) -> None:
        self._client.close()
