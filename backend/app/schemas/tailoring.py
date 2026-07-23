"""Schemas for resume tailoring & cover letters (Phase 8)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DraftAnswer(BaseModel):
    question: str
    answer: str


class TailorResult(BaseModel):
    """Structured output from the model (validated + retried)."""

    tailored_resume: str = Field(..., description="Full tailored resume text.")
    cover_letter: str = Field(..., description="Tailored cover letter.")
    draft_answers: list[DraftAnswer] = Field(default_factory=list)
    changes_summary: list[str] = Field(
        default_factory=list,
        description="Bullet list of what was emphasized/reordered — never invented.",
    )


class TailorRequest(BaseModel):
    resume_version_id: int | None = None  # if omitted, best match is picked
    questions: list[str] | None = None


class TailoredDocumentOut(BaseModel):
    id: int
    application_id: int
    source_resume_version_id: int | None
    status: str  # DRAFT | APPROVED
    approved_at: datetime | None
    before_resume: str  # original parsed text of the source version
    tailored_resume: str
    cover_letter: str
    draft_answers: list[DraftAnswer]
    changes_summary: list[str]
    created_at: datetime
    updated_at: datetime
