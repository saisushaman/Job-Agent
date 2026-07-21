"""AI routes (Phase 2): Ollama health + test prompt endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.base import AIProvider
from app.ai.deps import get_ai_provider
from app.ai.exceptions import AIProviderError
from app.ai.prompts import DEFAULT_SYSTEM
from app.schemas.ai import (
    AIHealthResponse,
    GreetingResult,
    StructuredTestResponse,
    TestPromptRequest,
    TestPromptResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/health", response_model=AIHealthResponse)
def ai_health(provider: AIProvider = Depends(get_ai_provider)) -> AIHealthResponse:
    """Report whether Ollama is reachable and the configured model is installed."""
    return AIHealthResponse(**provider.health())


@router.post("/test", response_model=TestPromptResponse)
def ai_test(
    body: TestPromptRequest,
    provider: AIProvider = Depends(get_ai_provider),
) -> TestPromptResponse:
    """Send a simple prompt to the local model and return its plain-text reply."""
    try:
        text = provider.generate(body.prompt, system=DEFAULT_SYSTEM)
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return TestPromptResponse(model=provider.model, prompt=body.prompt, response=text)


@router.post("/test-structured", response_model=StructuredTestResponse)
def ai_test_structured(
    provider: AIProvider = Depends(get_ai_provider),
) -> StructuredTestResponse:
    """Exercise structured JSON output + validation/retry against a small schema."""
    try:
        result = provider.generate_json(
            "Produce a friendly greeting and describe it.",
            GreetingResult,
            system=DEFAULT_SYSTEM,
        )
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return StructuredTestResponse(model=provider.model, result=result)
