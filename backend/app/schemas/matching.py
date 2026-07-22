"""Schemas for candidate profile and job matching (Phase 5)."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Recommendation(str, Enum):
    APPLY = "APPLY"
    REVIEW = "REVIEW"
    LOW_PRIORITY = "LOW_PRIORITY"
    DO_NOT_APPLY = "DO_NOT_APPLY"


# --- candidate profile ---


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str | None
    headline: str | None
    years_experience: float | None
    skills: list[str]
    languages: list[str]
    current_location: str | None
    current_country: str | None
    preferred_regions: list[str]
    needs_sponsorship: bool
    open_to_relocation: bool
    open_to_remote: bool


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    headline: str | None = None
    years_experience: float | None = None
    skills: list[str] | None = None
    languages: list[str] | None = None
    current_location: str | None = None
    current_country: str | None = None
    preferred_regions: list[str] | None = None
    needs_sponsorship: bool | None = None
    open_to_relocation: bool | None = None
    open_to_remote: bool | None = None


# --- match ---


class MatchWeights(BaseModel):
    technical: float = 0.35
    experience: float = 0.20
    sponsorship: float = 0.25
    location: float = 0.10
    language: float = 0.05
    relocation: float = 0.05


class MatchScores(BaseModel):
    technical: float
    experience: float
    sponsorship: float
    location: float
    language: float
    relocation: float


class MatchResult(BaseModel):
    scores: MatchScores
    overall_score: float
    recommendation: Recommendation
    reasoning: str
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    sponsorship_evidence: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    weights: MatchWeights


class MatchOut(BaseModel):
    job_id: int
    overall_score: float
    recommendation: Recommendation
    result: MatchResult
