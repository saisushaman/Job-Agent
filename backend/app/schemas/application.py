"""Schemas for the application tracker (Phase 7)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    job_id: int


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    external_application_id: str | None = None
    applied_at: datetime | None = None
    resume_version_id: int | None = None
    cover_letter: str | None = None
    recruiter_name: str | None = None
    recruiter_email: str | None = None
    recruiter_notes: str | None = None
    interview_at: datetime | None = None
    rejection_reason: str | None = None
    offer_details: str | None = None
    offer_salary: float | None = None


class ApplicationCard(BaseModel):
    """Compact shape for the list / Kanban board."""

    id: int
    job_id: int
    job_title: str
    job_company: str
    status: str
    match_score: float | None
    recommendation: str | None
    eligibility: str | None
    applied_at: datetime | None
    updated_at: datetime


class ApplicationEventOut(BaseModel):
    id: int
    event_type: str
    from_status: str | None
    to_status: str | None
    message: str | None
    created_at: datetime


class ApplicationDetail(BaseModel):
    id: int
    job_id: int
    job_title: str
    job_company: str
    status: str
    notes: str | None
    external_application_id: str | None
    applied_at: datetime | None
    resume_version_id: int | None
    cover_letter: str | None
    recruiter_name: str | None
    recruiter_email: str | None
    recruiter_notes: str | None
    interview_at: datetime | None
    rejection_reason: str | None
    offer_details: str | None
    offer_salary: float | None
    created_at: datetime
    updated_at: datetime
    events: list[ApplicationEventOut]
