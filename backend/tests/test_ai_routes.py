"""Tests for the AI routes using a fake provider injected via dependency override."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.ai.base import AIProvider
from app.ai.deps import get_ai_provider
from app.ai.exceptions import AIUnavailableError
from app.main import app
from app.schemas.ai import GreetingResult


class FakeProvider(AIProvider):
    model = "fake-model"

    def __init__(self, *, available: bool = True) -> None:
        self._available = available

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        if not self._available:
            raise AIUnavailableError("down")
        return f"echo: {prompt}"

    def generate_json(self, prompt, schema, *, system=None, max_retries=None):
        return schema.model_validate(
            {"greeting": "Hello!", "language": "English", "word_count": 1}
        )

    def embed(self, text: str) -> list[float]:
        return [0.0, 1.0]

    def health(self) -> dict:
        return {
            "available": self._available,
            "base_url": "http://fake",
            "model": self.model,
            "model_available": self._available,
            "models": ["fake-model"] if self._available else [],
        }


def _override(provider: AIProvider):
    app.dependency_overrides[get_ai_provider] = lambda: provider


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_ai_health_available() -> None:
    _override(FakeProvider(available=True))
    resp = TestClient(app).get("/api/ai/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is True
    assert body["model_available"] is True


def test_ai_test_prompt() -> None:
    _override(FakeProvider())
    resp = TestClient(app).post("/api/ai/test", json={"prompt": "hello"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["response"] == "echo: hello"
    assert body["model"] == "fake-model"


def test_ai_test_prompt_requires_nonempty() -> None:
    _override(FakeProvider())
    resp = TestClient(app).post("/api/ai/test", json={"prompt": ""})
    assert resp.status_code == 422  # validation error


def test_ai_test_unavailable_returns_503() -> None:
    _override(FakeProvider(available=False))
    resp = TestClient(app).post("/api/ai/test", json={"prompt": "hello"})
    assert resp.status_code == 503


def test_ai_test_structured() -> None:
    _override(FakeProvider())
    resp = TestClient(app).post("/api/ai/test-structured")
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert GreetingResult.model_validate(result).language == "English"
