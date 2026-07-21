"""Schemas for the resume system (Phase 3)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeVersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: int
    original_filename: str
    content_type: str | None
    file_size: int
    created_at: datetime


class ResumeVersionDetail(ResumeVersionSummary):
    parsed_text: str


class ResumeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    name: str
    version_count: int
    latest_version_number: int | None


class ResumeDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    name: str
    versions: list[ResumeVersionSummary]
