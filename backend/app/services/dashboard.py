"""Dashboard aggregation + job search (Phase 6)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.application_statuses import APPLICATION_STATUSES
from app.models.application import Application
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.job_match import JobMatch
from app.schemas.dashboard import DashboardStats, JobListItem, TopMatch
from app.schemas.matching import Recommendation


def _count_group(db: Session, column) -> dict[str, int]:
    rows = db.execute(
        select(column, func.count()).group_by(column)
    ).all()
    return {str(value): count for value, count in rows if value is not None}


def build_stats(db: Session, top_n: int = 5) -> DashboardStats:
    total_jobs = db.scalar(select(func.count(Job.id))) or 0
    analyzed = db.scalar(select(func.count(JobAnalysis.id))) or 0
    matched = db.scalar(select(func.count(JobMatch.id))) or 0

    # Pipeline: application status counts, all statuses present (default 0).
    pipeline = {status: 0 for status in APPLICATION_STATUSES}
    for status, count in db.execute(
        select(Application.status, func.count()).group_by(Application.status)
    ).all():
        pipeline[status] = count

    recommendations = {r.value: 0 for r in Recommendation}
    recommendations.update(_count_group(db, JobMatch.recommendation))

    regions = _count_group(db, JobAnalysis.region)
    eligibility = _count_group(db, JobAnalysis.eligibility)
    sponsorship_us = _count_group(db, JobAnalysis.sponsorship_us)
    visa_eu = _count_group(db, JobAnalysis.visa_support_eu)

    top_rows = db.execute(
        select(JobMatch, Job)
        .join(Job, Job.id == JobMatch.job_id)
        .where(JobMatch.recommendation != Recommendation.DO_NOT_APPLY.value)
        .order_by(JobMatch.overall_score.desc())
        .limit(top_n)
    ).all()
    top_matches = [
        TopMatch(
            job_id=job.id,
            title=job.title,
            company=job.company,
            overall_score=match.overall_score,
            recommendation=match.recommendation,
            region=job.analysis.region if job.analysis else None,
            eligibility=job.analysis.eligibility if job.analysis else None,
        )
        for match, job in top_rows
    ]

    return DashboardStats(
        total_jobs=total_jobs,
        analyzed=analyzed,
        matched=matched,
        pipeline=pipeline,
        recommendations=recommendations,
        regions=regions,
        eligibility=eligibility,
        usa_total=regions.get("USA", 0),
        europe_total=regions.get("EUROPE", 0),
        sponsorship_us=sponsorship_us,
        visa_eu=visa_eu,
        top_matches=top_matches,
    )


def search_jobs(
    db: Session,
    *,
    q: str | None = None,
    region: str | None = None,
    country: str | None = None,
    company: str | None = None,
    eligibility: str | None = None,
    recommendation: str | None = None,
    min_score: float | None = None,
    remote_only: bool = False,
) -> list[JobListItem]:
    stmt = (
        select(Job)
        .outerjoin(JobAnalysis, JobAnalysis.job_id == Job.id)
        .outerjoin(JobMatch, JobMatch.job_id == Job.id)
        .options(selectinload(Job.analysis), selectinload(Job.match))
        .order_by(Job.id.desc())
    )

    if q:
        like = f"%{q}%"
        stmt = stmt.where(Job.title.ilike(like) | Job.company.ilike(like))
    if country:
        stmt = stmt.where(Job.country.ilike(f"%{country}%"))
    if company:
        stmt = stmt.where(Job.company.ilike(f"%{company}%"))
    if region:
        stmt = stmt.where(JobAnalysis.region == region)
    if eligibility:
        stmt = stmt.where(JobAnalysis.eligibility == eligibility)
    if recommendation:
        stmt = stmt.where(JobMatch.recommendation == recommendation)
    if min_score is not None:
        stmt = stmt.where(JobMatch.overall_score >= min_score)

    jobs = db.scalars(stmt).unique().all()

    items: list[JobListItem] = []
    for job in jobs:
        a = job.analysis
        m = job.match
        relocation = (a.data.get("relocation") if a else None) or None
        is_remote = relocation == "REMOTE"
        if remote_only and not is_remote:
            continue
        items.append(
            JobListItem(
                id=job.id,
                title=job.title,
                company=job.company,
                country=job.country,
                city=job.city,
                url=job.url,
                description=job.description,
                analyzed=a is not None,
                matched=m is not None,
                region=a.region if a else None,
                eligibility=a.eligibility if a else None,
                sponsorship_us=a.sponsorship_us if a else None,
                visa_support_eu=a.visa_support_eu if a else None,
                remote=is_remote,
                match_score=m.overall_score if m else None,
                recommendation=m.recommendation if m else None,
            )
        )
    return items
