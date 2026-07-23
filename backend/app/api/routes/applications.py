"""Application tracker routes (Phase 7)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status as http
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.application_statuses import APPLICATION_STATUSES
from app.database.session import get_db
from app.models.application import Application, ApplicationEvent
from app.models.job import Job
from app.schemas.application import (
    ApplicationCard,
    ApplicationCreate,
    ApplicationDetail,
    ApplicationEventOut,
    ApplicationUpdate,
)

router = APIRouter(prefix="/applications", tags=["applications"])

# Statuses that mean "actively applying" — blocked for NOT_ELIGIBLE jobs.
APPLY_LOCKED_STATUSES = {"APPLICATION_READY", "APPLYING", "APPLIED"}


def _job_eligibility(job: Job) -> str | None:
    return job.analysis.eligibility if job.analysis else None


def _card(app: Application) -> ApplicationCard:
    job = app.job
    return ApplicationCard(
        id=app.id,
        job_id=app.job_id,
        job_title=job.title,
        job_company=job.company,
        status=app.status,
        match_score=job.match.overall_score if job.match else None,
        recommendation=job.match.recommendation if job.match else None,
        eligibility=_job_eligibility(job),
        applied_at=app.applied_at,
        updated_at=app.updated_at,
    )


def _detail(app: Application) -> ApplicationDetail:
    return ApplicationDetail(
        id=app.id,
        job_id=app.job_id,
        job_title=app.job.title,
        job_company=app.job.company,
        status=app.status,
        notes=app.notes,
        external_application_id=app.external_application_id,
        applied_at=app.applied_at,
        resume_version_id=app.resume_version_id,
        cover_letter=app.cover_letter,
        recruiter_name=app.recruiter_name,
        recruiter_email=app.recruiter_email,
        recruiter_notes=app.recruiter_notes,
        interview_at=app.interview_at,
        rejection_reason=app.rejection_reason,
        offer_details=app.offer_details,
        offer_salary=app.offer_salary,
        created_at=app.created_at,
        updated_at=app.updated_at,
        events=[
            ApplicationEventOut(
                id=e.id,
                event_type=e.event_type,
                from_status=e.from_status,
                to_status=e.to_status,
                message=e.message,
                created_at=e.created_at,
            )
            for e in app.events
        ],
    )


def _get_or_404(db: Session, application_id: int) -> Application:
    app = db.get(Application, application_id)
    if app is None:
        raise HTTPException(http.HTTP_404_NOT_FOUND, "Application not found")
    return app


@router.get("", response_model=list[ApplicationCard])
def list_applications(
    status_filter: str | None = None, db: Session = Depends(get_db)
) -> list[ApplicationCard]:
    stmt = (
        select(Application)
        .options(
            selectinload(Application.job).selectinload(Job.match),
            selectinload(Application.job).selectinload(Job.analysis),
        )
        .order_by(Application.updated_at.desc())
    )
    if status_filter:
        stmt = stmt.where(Application.status == status_filter)
    return [_card(a) for a in db.scalars(stmt).unique().all()]


@router.post("", response_model=ApplicationDetail, status_code=http.HTTP_201_CREATED)
def create_application(
    body: ApplicationCreate, db: Session = Depends(get_db)
) -> ApplicationDetail:
    job = db.get(Job, body.job_id)
    if job is None:
        raise HTTPException(http.HTTP_404_NOT_FOUND, "Job not found")

    existing = db.scalar(
        select(Application).where(Application.job_id == job.id)
    )
    if existing is not None:
        raise HTTPException(
            http.HTTP_409_CONFLICT, "An application already exists for this job"
        )

    # Default status respects the citizenship / eligibility rule.
    initial = "NOT_ELIGIBLE" if _job_eligibility(job) == "NOT_ELIGIBLE" else "DISCOVERED"
    app = Application(job_id=job.id, status=initial)
    db.add(app)
    db.flush()
    db.add(
        ApplicationEvent(
            application_id=app.id,
            event_type="CREATED",
            to_status=initial,
            message="Application added to tracker",
        )
    )
    db.commit()
    db.refresh(app)
    return _detail(app)


@router.get("/{application_id}", response_model=ApplicationDetail)
def get_application(application_id: int, db: Session = Depends(get_db)) -> ApplicationDetail:
    return _detail(_get_or_404(db, application_id))


@router.patch("/{application_id}", response_model=ApplicationDetail)
def update_application(
    application_id: int, body: ApplicationUpdate, db: Session = Depends(get_db)
) -> ApplicationDetail:
    app = _get_or_404(db, application_id)
    data = body.model_dump(exclude_unset=True)

    new_status = data.get("status")
    if new_status is not None and new_status != app.status:
        if new_status not in APPLICATION_STATUSES:
            raise HTTPException(
                http.HTTP_422_UNPROCESSABLE_ENTITY, f"Unknown status '{new_status}'"
            )
        if (
            new_status in APPLY_LOCKED_STATUSES
            and _job_eligibility(app.job) == "NOT_ELIGIBLE"
        ):
            raise HTTPException(
                http.HTTP_400_BAD_REQUEST,
                "Job is NOT_ELIGIBLE (citizenship / no sponsorship) — cannot move it "
                f"to {new_status}.",
            )
        from_status = app.status
        app.status = new_status
        # Auto-stamp applied_at when moving to APPLIED.
        if new_status == "APPLIED" and app.applied_at is None and "applied_at" not in data:
            app.applied_at = datetime.now(timezone.utc)
        db.add(
            ApplicationEvent(
                application_id=app.id,
                event_type="STATUS_CHANGE",
                from_status=from_status,
                to_status=new_status,
            )
        )

    for field, value in data.items():
        if field == "status":
            continue
        setattr(app, field, value)

    db.commit()
    db.refresh(app)
    return _detail(app)


@router.get("/{application_id}/events", response_model=list[ApplicationEventOut])
def list_events(
    application_id: int, db: Session = Depends(get_db)
) -> list[ApplicationEventOut]:
    app = _get_or_404(db, application_id)
    return [
        ApplicationEventOut(
            id=e.id,
            event_type=e.event_type,
            from_status=e.from_status,
            to_status=e.to_status,
            message=e.message,
            created_at=e.created_at,
        )
        for e in app.events
    ]
