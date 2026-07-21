"""Unit tests for OllamaProvider using a mocked Ollama HTTP backend.

No real Ollama is contacted — httpx.MockTransport routes requests to canned responses.
"""

from __future__ import annotations

import json

import httpx
import pytest

from app.ai.exceptions import AIUnavailableError, InvalidJSONError
from app.ai.providers import OllamaProvider
from app.schemas.ai import GreetingResult


def make_provider(handler) -> OllamaProvider:
    client = httpx.Client(
        base_url="http://test-ollama", transport=httpx.MockTransport(handler)
    )
    return OllamaProvider(
        base_url="http://test-ollama",
        model="qwen3:8b",
        embedding_model="nomic-embed-text",
        max_retries=2,
        client=client,
    )


def _chat_response(content: str) -> httpx.Response:
    return httpx.Response(200, json={"message": {"role": "assistant", "content": content}})


def test_generate_returns_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        return _chat_response("Hello there!")

    provider = make_provider(handler)
    assert provider.generate("hi") == "Hello there!"


def test_generate_strips_think_block() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return _chat_response("<think>reasoning...</think>Final answer.")

    provider = make_provider(handler)
    assert provider.generate("hi") == "Final answer."


def test_generate_json_valid() -> None:
    payload = {"greeting": "Hello!", "language": "English", "word_count": 1}

    def handler(request: httpx.Request) -> httpx.Response:
        return _chat_response(json.dumps(payload))

    provider = make_provider(handler)
    result = provider.generate_json("greet me", GreetingResult)
    assert isinstance(result, GreetingResult)
    assert result.language == "English"


def test_generate_json_retries_then_succeeds() -> None:
    calls = {"n": 0}
    good = {"greeting": "Hi", "language": "English", "word_count": 1}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return _chat_response("not json at all")
        return _chat_response(json.dumps(good))

    provider = make_provider(handler)
    result = provider.generate_json("greet me", GreetingResult)
    assert result.greeting == "Hi"
    assert calls["n"] == 2  # retried exactly once


def test_generate_json_exhausts_retries() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return _chat_response("still not json")

    provider = make_provider(handler)
    with pytest.raises(InvalidJSONError):
        provider.generate_json("greet me", GreetingResult, max_retries=1)


def test_health_available_with_model() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/tags"
        return httpx.Response(
            200, json={"models": [{"name": "qwen3:8b"}, {"name": "nomic-embed-text"}]}
        )

    provider = make_provider(handler)
    health = provider.health()
    assert health["available"] is True
    assert health["model_available"] is True
    assert "qwen3:8b" in health["models"]


def test_health_unavailable_on_connection_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    provider = make_provider(handler)
    health = provider.health()
    assert health["available"] is False
    assert health["model_available"] is False


def test_post_error_raises_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    provider = make_provider(handler)
    with pytest.raises(AIUnavailableError):
        provider.generate("hi")


def test_embed_returns_vector() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/embeddings"
        return httpx.Response(200, json={"embedding": [0.1, 0.2, 0.3]})

    provider = make_provider(handler)
    assert provider.embed("some text") == [0.1, 0.2, 0.3]
