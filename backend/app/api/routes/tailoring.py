"""Resume tailoring & cover letter routes (Phase 8)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status as http
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.base import AIProvider
from app.ai.deps import get_ai_provider
from app.ai.exceptions import AIProviderError
from app.database.session import get_db
from app.models.application import Application, ApplicationEvent
from app.models.resume import ResumeVersion
from app.models.tailored_document import (
    STATUS_APPROVED,
    STATUS_DRAFT,
    TailoredDocument,
)
from app.schemas.tailoring import (
    DraftAnswer,
    TailoredDocumentOut,
    TailorRequest,
)
from app.services.profile import get_or_create_profile
from app.services.tailoring import (
    DOCX_MEDIA,
    pick_best_resume_version,
    tailor,
    text_to_docx_bytes,
)

router = APIRouter(prefix="/applications", tags=["tailoring"])


def _get_application_or_404(db: Session, application_id: int) -> Application:
    app = db.get(Application, application_id)
    if app is None:
        raise HTTPException(http.HTTP_404_NOT_FOUND, "Application not found")
    return app


def _out(db: Session, doc: TailoredDocument) -> TailoredDocumentOut:
    before = ""
    if doc.source_resume_version_id is not None:
        version = db.get(ResumeVersion, doc.source_resume_version_id)
        if version is not None:
            before = version.parsed_text or ""
    return TailoredDocumentOut(
        id=doc.id,
        application_id=doc.application_id,
        source_resume_version_id=doc.source_resume_version_id,
        status=doc.status,
        approved_at=doc.approved_at,
        before_resume=before,
        tailored_resume=doc.tailored_resume,
        cover_letter=doc.cover_letter,
        draft_answers=[DraftAnswer(**a) for a in (doc.draft_answers or [])],
        changes_summary=list(doc.changes_summary or []),
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.post("/{application_id}/tailor", response_model=TailoredDocumentOut)
def generate_tailored(
    application_id: int,
    body: TailorRequest,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
) -> TailoredDocumentOut:
    app = _get_application_or_404(db, application_id)
    job = app.job

    if job.analysis is not None and job.analysis.eligibility == "NOT_ELIGIBLE":
        raise HTTPException(
            http.HTTP_400_BAD_REQUEST,
            "Job is NOT_ELIGIBLE (citizenship / no sponsorship) — tailoring is disabled.",
        )

    if body.resume_version_id is not None:
        version = db.get(ResumeVersion, body.resume_version_id)
        if version is None:
            raise HTTPException(http.HTTP_404_NOT_FOUND, "Resume version not found")
    else:
        version = pick_best_resume_version(provider, db, job)
        if version is None:
            raise HTTPException(
                http.HTTP_400_BAD_REQUEST,
                "No resume uploaded yet — add one on the Resumes page first.",
            )

    profile = get_or_create_profile(db)
    try:
        result = tailor(
            provider,
            resume_version=version,
            profile=profile,
            job=job,
            questions=body.questions or [],
        )
    except AIProviderError as exc:
        raise HTTPException(
            http.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    doc = db.scalar(
        select(TailoredDocument).where(
            TailoredDocument.application_id == app.id
        )
    )
    if doc is None:
        doc = TailoredDocument(application_id=app.id)
        db.add(doc)

    doc.source_resume_version_id = version.id
    doc.status = STATUS_DRAFT
    doc.approved_at = None
    doc.tailored_resume = result.tailored_resume
    doc.cover_letter = result.cover_letter
    doc.draft_answers = [a.model_dump() for a in result.draft_answers]
    doc.changes_summary = result.changes_summary

    db.commit()
    db.refresh(doc)
    return _out(db, doc)


@router.get("/{application_id}/tailor", response_model=TailoredDocumentOut)
def get_tailored(
    application_id: int, db: Session = Depends(get_db)
) -> TailoredDocumentOut:
    _get_application_or_404(db, application_id)
    doc = db.scalar(
        select(TailoredDocument).where(
            TailoredDocument.application_id == application_id
        )
    )
    if doc is None:
        raise HTTPException(http.HTTP_404_NOT_FOUND, "No tailored draft yet")
    return _out(db, doc)


@router.post("/{application_id}/tailor/approve", response_model=TailoredDocumentOut)
def approve_tailored(
    application_id: int, db: Session = Depends(get_db)
) -> TailoredDocumentOut:
    app = _get_application_or_404(db, application_id)
    doc = db.scalar(
        select(TailoredDocument).where(
            TailoredDocument.application_id == application_id
        )
    )
    if doc is None:
        raise HTTPException(http.HTTP_404_NOT_FOUND, "No tailored draft to approve")

    doc.status = STATUS_APPROVED
    doc.approved_at = datetime.now(timezone.utc)

    # Approving readies the application (unless the job is not eligible).
    eligible = not (app.job.analysis and app.job.analysis.eligibility == "NOT_ELIGIBLE")
    if eligible and app.status in {"DISCOVERED", "REVIEW", "APPROVED"}:
        from_status = app.status
        app.status = "APPLICATION_READY"
        db.add(
            ApplicationEvent(
                application_id=app.id,
                event_type="STATUS_CHANGE",
                from_status=from_status,
                to_status="APPLICATION_READY",
                message="Tailored documents approved",
            )
        )

    db.commit()
    db.refresh(doc)
    return _out(db, doc)


@router.get("/{application_id}/tailor/document")
def download_document(
    application_id: int,
    kind: str = "resume",
    fmt: str = "txt",
    db: Session = Depends(get_db),
) -> Response:
    _get_application_or_404(db, application_id)
    doc = db.scalar(
        select(TailoredDocument).where(
            TailoredDocument.application_id == application_id
        )
    )
    if doc is None:
        raise HTTPException(http.HTTP_404_NOT_FOUND, "No tailored document")
    if kind not in {"resume", "cover_letter"}:
        raise HTTPException(http.HTTP_400_BAD_REQUEST, "kind must be resume|cover_letter")
    if fmt not in {"txt", "md", "docx"}:
        raise HTTPException(http.HTTP_400_BAD_REQUEST, "fmt must be txt|md|docx")

    text = doc.tailored_resume if kind == "resume" else doc.cover_letter
    filename = f"{kind}.{fmt}"

    if fmt == "docx":
        data = text_to_docx_bytes(text)
        media = DOCX_MEDIA
    else:
        data = text.encode("utf-8")
        media = "text/markdown" if fmt == "md" else "text/plain"

    return Response(
        content=data,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
