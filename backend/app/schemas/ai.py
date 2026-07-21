"""Schemas for the AI test/health endpoints (Phase 2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AIHealthResponse(BaseModel):
    available: bool
    base_url: str
    model: str
    model_available: bool
    models: list[str]


class TestPromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, examples=["Say hello in one short sentence."])


class TestPromptResponse(BaseModel):
    model: str
    prompt: str
    response: str


# --- structured-output demo (exercises JSON validation + retry) ---


class GreetingResult(BaseModel):
    """Small schema the model must fill for the structured test endpoint."""

    greeting: str = Field(..., description="A short greeting sentence.")
    language: str = Field(..., description="Language of the greeting, e.g. 'English'.")
    word_count: int = Field(..., ge=0, description="Number of words in the greeting.")


class StructuredTestResponse(BaseModel):
    model: str
    result: GreetingResult
