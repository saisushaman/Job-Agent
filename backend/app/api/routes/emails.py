"""Email routes (Phase 9): sync, classify, list, detail, manual override, status.

Never deletes email — there is no delete endpoint, and the Gmail provider uses a
read-only scope.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status as http
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.base import AIProvider
from app.ai.deps import get_ai_provider
from app.ai.exceptions import AIProviderError
from app.config import settings
from app.database.session import get_db
from app.email.base import EmailNotConfiguredError, EmailProvider
from app.email.deps import get_email_provider
from app.models.application import Application, ApplicationEvent
from app.models.email_message import EmailMessage
from app.schemas.email import (
    ClassifyResult,
    EmailCategory,
    EmailDetail,
    EmailOut,
    EmailPatch,
    EmailProviderStatus,
    SyncResult,
)
from app.services.email_classifier import (
    CATEGORY_TO_STATUS,
    classify_email,
    match_application,
)

router = APIRouter(prefix="/emails", tags=["emails"])

APPLY_LOCKED = {"APPLICATION_READY", "APPLYING", "APPLIED"}


def _out(email: EmailMessage) -> EmailOut:
    return EmailOut(
        id=email.id,
        external_id=email.external_id,
        sender=email.sender,
        sender_email=email.sender_email,
        subject=email.subject,
        snippet=email.snippet,
        received_at=email.received_at,
        classified=email.classified,
        category=email.category,
        confidence=email.confidence,
        needs_review=email.needs_review,
        application_id=email.application_id,
        application_job_title=email.application.job.title if email.application else None,
    )


@router.get("/status", response_model=EmailProviderStatus)
def email_status(
    provider: EmailProvider = Depends(get_email_provider),
) -> EmailProviderStatus:
    return EmailProviderStatus(**provider.status())


@router.post("/sync", response_model=SyncResult)
def sync_emails(
    limit: int = 50,
    db: Session = Depends(get_db),
    provider: EmailProvider = Depends(get_email_provider),
) -> SyncResult:
    try:
        raw = provider.fetch(limit=limit)
    except EmailNotConfiguredError as exc:
        raise HTTPException(http.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    existing = set(db.scalars(select(EmailMessage.external_id)).all())
    new_count = 0
    for r in raw:
        if r.external_id in existing:
            continue
        db.add(
            EmailMessage(
                external_id=r.external_id,
                thread_id=r.thread_id,
                sender=r.sender,
                sender_email=r.sender_email,
                subject=r.subject,
                snippet=r.snippet,
                body=r.body,
                received_at=r.received_at,
            )
        )
        new_count += 1
    db.commit()
    return SyncResult(provider=provider.name, fetched=len(raw), new=new_count)


@router.post("/classify", response_model=ClassifyResult)
def classify_emails(
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
) -> ClassifyResult:
    emails = db.scalars(
        select(EmailMessage).where(EmailMessage.classified.is_(False))
    ).all()

    classified = needs_review = matched = status_updates = 0
    threshold = settings.email_classify_confidence_threshold

    for email in emails:
        try:
            result = classify_email(provider, email)
        except AIProviderError as exc:
            raise HTTPException(
                http.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
            ) from exc

        email.category = result.category.value
        email.confidence = result.confidence
        email.needs_review = result.confidence < threshold
        email.classified = True
        classified += 1
        if email.needs_review:
            needs_review += 1

        app = match_application(db, email)
        if app is not None:
            email.application_id = app.id
            matched += 1
            new_status = CATEGORY_TO_STATUS.get(result.category.value)
            job_not_eligible = bool(
                app.job.analysis and app.job.analysis.eligibility == "NOT_ELIGIBLE"
            )
            # Auto-advance status only when confident, and never push a NOT_ELIGIBLE
            # job into an apply column.
            if (
                new_status
                and not email.needs_review
                and app.status != new_status
                and not (new_status in APPLY_LOCKED and job_not_eligible)
            ):
                from_status = app.status
                app.status = new_status
                db.add(
                    ApplicationEvent(
                        application_id=app.id,
                        event_type="EMAIL",
                        from_status=from_status,
                        to_status=new_status,
                        message=f"Auto-updated from email: {email.subject}",
                    )
                )
                status_updates += 1

    db.commit()
    return ClassifyResult(
        classified=classified,
        needs_review=needs_review,
        matched=matched,
        status_updates=status_updates,
    )


@router.get("", response_model=list[EmailOut])
def list_emails(
    category: str | None = None,
    needs_review: bool | None = None,
    db: Session = Depends(get_db),
) -> list[EmailOut]:
    stmt = select(EmailMessage).order_by(EmailMessage.received_at.desc().nullslast())
    if category:
        stmt = stmt.where(EmailMessage.category == category)
    if needs_review is not None:
        stmt = stmt.where(EmailMessage.needs_review.is_(needs_review))
    return [_out(e) for e in db.scalars(stmt).all()]


def _get_or_404(db: Session, email_id: int) -> EmailMessage:
    email = db.get(EmailMessage, email_id)
    if email is None:
        raise HTTPException(http.HTTP_404_NOT_FOUND, "Email not found")
    return email


@router.get("/{email_id}", response_model=EmailDetail)
def get_email(email_id: int, db: Session = Depends(get_db)) -> EmailDetail:
    email = _get_or_404(db, email_id)
    return EmailDetail(**_out(email).model_dump(), body=email.body)


@router.patch("/{email_id}", response_model=EmailOut)
def patch_email(
    email_id: int, body: EmailPatch, db: Session = Depends(get_db)
) -> EmailOut:
    email = _get_or_404(db, email_id)
    data = body.model_dump(exclude_unset=True)
    if "category" in data and data["category"] is not None:
        if data["category"] not in {c.value for c in EmailCategory}:
            raise HTTPException(
                http.HTTP_422_UNPROCESSABLE_ENTITY, "Unknown category"
            )
        email.category = data["category"]
        email.classified = True
        email.needs_review = False  # human reviewed
    if "application_id" in data:
        email.application_id = data["application_id"]
    if "needs_review" in data and data["needs_review"] is not None:
        email.needs_review = data["needs_review"]
    db.commit()
    db.refresh(email)
    return _out(email)
