"""Schemas for email sync/classification (Phase 9)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class EmailCategory(str, Enum):
    APPLICATION_CONFIRMATION = "APPLICATION_CONFIRMATION"
    RECRUITER_CONTACT = "RECRUITER_CONTACT"
    INTERVIEW = "INTERVIEW"
    ASSESSMENT = "ASSESSMENT"
    REJECTION = "REJECTION"
    OFFER = "OFFER"
    FOLLOW_UP = "FOLLOW_UP"
    OTHER = "OTHER"


class EmailClassificationResult(BaseModel):
    """Structured output from the model."""

    category: EmailCategory = EmailCategory.OTHER
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    reason: str = ""


class EmailOut(BaseModel):
    id: int
    external_id: str
    sender: str
    sender_email: str
    subject: str
    snippet: str
    received_at: datetime | None
    classified: bool
    category: str | None
    confidence: float | None
    needs_review: bool
    application_id: int | None
    application_job_title: str | None


class EmailDetail(EmailOut):
    body: str


class EmailPatch(BaseModel):
    category: str | None = None
    application_id: int | None = None
    needs_review: bool | None = None


class SyncResult(BaseModel):
    provider: str
    fetched: int
    new: int


class ClassifyResult(BaseModel):
    classified: int
    needs_review: int
    matched: int
    status_updates: int


class EmailProviderStatus(BaseModel):
    provider: str
    configured: bool
    detail: str
