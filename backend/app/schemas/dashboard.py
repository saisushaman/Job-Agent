"""Schemas for the dashboard stats and job search (Phase 6)."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.job_analysis import JobAnalysisOut, JobOut
from app.schemas.matching import MatchOut


class TopMatch(BaseModel):
    job_id: int
    title: str
    company: str
    overall_score: float
    recommendation: str
    region: str | None
    eligibility: str | None


class DashboardStats(BaseModel):
    total_jobs: int
    analyzed: int
    matched: int
    # Application pipeline counts keyed by status (all statuses present, default 0).
    pipeline: dict[str, int]
    # Match recommendation counts (APPLY/REVIEW/LOW_PRIORITY/DO_NOT_APPLY).
    recommendations: dict[str, int]
    # Analyzed-job region counts (USA/EUROPE/OTHER/UNKNOWN).
    regions: dict[str, int]
    # Eligibility counts (ELIGIBLE/REVIEW/NOT_ELIGIBLE).
    eligibility: dict[str, int]
    usa_total: int
    europe_total: int
    sponsorship_us: dict[str, int]
    visa_eu: dict[str, int]
    top_matches: list[TopMatch]


class JobListItem(BaseModel):
    id: int
    title: str
    company: str
    country: str | None
    city: str | None
    url: str | None
    description: str | None
    analyzed: bool
    matched: bool
    region: str | None
    eligibility: str | None
    sponsorship_us: str | None
    visa_support_eu: str | None
    remote: bool
    match_score: float | None
    recommendation: str | None


class JobDetail(BaseModel):
    job: JobOut
    analysis: JobAnalysisOut | None
    match: MatchOut | None
