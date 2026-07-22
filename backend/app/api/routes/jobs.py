"""Job routes (Phase 4): manual job import + Qwen3 analysis."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.base import AIProvider
from app.ai.deps import get_ai_provider
from app.ai.exceptions import AIProviderError
from app.database.session import get_db
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.job_match import JobMatch
from app.schemas.job_analysis import (
    Eligibility,
    JobAnalysisOut,
    JobAnalysisResult,
    JobCreate,
    JobOut,
    Region,
)
from app.schemas.matching import (
    MatchOut,
    MatchResult,
    MatchWeights,
    Recommendation,
)
from app.services.job_analysis import analyze_job
from app.services.matching import match_job
from app.services.profile import get_or_create_profile

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_job_or_404(db: Session, job_id: int) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(body: JobCreate, db: Session = Depends(get_db)) -> Job:
    job = Job(**body.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return list(db.scalars(select(Job).order_by(Job.id.desc())).all())


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)) -> Job:
    return _get_job_or_404(db, job_id)


def _to_out(analysis: JobAnalysis) -> JobAnalysisOut:
    return JobAnalysisOut(
        job_id=analysis.job_id,
        region=Region(analysis.region),
        eligibility=Eligibility(analysis.eligibility),
        citizenship_required=analysis.citizenship_required,
        result=JobAnalysisResult.model_validate(analysis.data),
    )


@router.post("/{job_id}/analyze", response_model=JobAnalysisOut)
def analyze(
    job_id: int,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
) -> JobAnalysisOut:
    job = _get_job_or_404(db, job_id)
    try:
        result = analyze_job(provider, job)
    except AIProviderError as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    analysis = db.scalar(
        select(JobAnalysis).where(JobAnalysis.job_id == job.id)
    )
    if analysis is None:
        analysis = JobAnalysis(job_id=job.id)
        db.add(analysis)

    analysis.region = result.region.value
    analysis.sponsorship_us = (
        result.sponsorship_us.value if result.sponsorship_us else None
    )
    analysis.visa_support_eu = (
        result.visa_support_eu.value if result.visa_support_eu else None
    )
    analysis.eligibility = result.eligibility.value
    analysis.citizenship_required = result.citizenship_required
    analysis.work_authorization_required = result.work_authorization_required
    analysis.summary = result.summary
    analysis.data = result.model_dump(mode="json")

    db.commit()
    db.refresh(analysis)
    return _to_out(analysis)


@router.get("/{job_id}/analysis", response_model=JobAnalysisOut)
def get_analysis(job_id: int, db: Session = Depends(get_db)) -> JobAnalysisOut:
    _get_job_or_404(db, job_id)
    analysis = db.scalar(select(JobAnalysis).where(JobAnalysis.job_id == job_id))
    if analysis is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Job has not been analyzed yet"
        )
    return _to_out(analysis)


def _match_to_out(match: JobMatch) -> MatchOut:
    return MatchOut(
        job_id=match.job_id,
        overall_score=match.overall_score,
        recommendation=Recommendation(match.recommendation),
        result=MatchResult.model_validate(match.data),
    )


@router.post("/{job_id}/match", response_model=MatchOut)
def match(
    job_id: int,
    weights: MatchWeights | None = None,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
) -> MatchOut:
    job = _get_job_or_404(db, job_id)
    analysis_row = db.scalar(select(JobAnalysis).where(JobAnalysis.job_id == job.id))
    if analysis_row is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Analyze the job first (POST /api/jobs/{id}/analyze) before matching.",
        )

    analysis = JobAnalysisResult.model_validate(analysis_row.data)
    profile = get_or_create_profile(db)

    try:
        result = match_job(
            provider,
            profile,
            job,
            analysis,
            Eligibility(analysis_row.eligibility),
            weights,
        )
    except AIProviderError as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    match_row = db.scalar(select(JobMatch).where(JobMatch.job_id == job.id))
    if match_row is None:
        match_row = JobMatch(job_id=job.id)
        db.add(match_row)
    match_row.overall_score = result.overall_score
    match_row.recommendation = result.recommendation.value
    match_row.data = result.model_dump(mode="json")

    db.commit()
    db.refresh(match_row)
    return _match_to_out(match_row)


@router.get("/{job_id}/match", response_model=MatchOut)
def get_match(job_id: int, db: Session = Depends(get_db)) -> MatchOut:
    _get_job_or_404(db, job_id)
    match_row = db.scalar(select(JobMatch).where(JobMatch.job_id == job_id))
    if match_row is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Job has not been matched yet"
        )
    return _match_to_out(match_row)
