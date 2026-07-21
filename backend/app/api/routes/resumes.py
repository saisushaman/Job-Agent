"""Resume routes (Phase 3): tracks, uploads, versions, preview, download."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.models.resume import Resume, ResumeVersion
from app.schemas.resume import (
    ResumeDetail,
    ResumeSummary,
    ResumeVersionDetail,
    ResumeVersionSummary,
)
from app.services.resume_parser import (
    SUPPORTED_EXTENSIONS,
    UnsupportedResumeType,
    parse_resume,
)

router = APIRouter(prefix="/resumes", tags=["resumes"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


def _get_resume_or_404(db: Session, resume_id: int) -> Resume:
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume track not found")
    return resume


@router.get("", response_model=list[ResumeSummary])
def list_resumes(db: Session = Depends(get_db)) -> list[ResumeSummary]:
    resumes = db.scalars(select(Resume).order_by(Resume.id)).all()
    out: list[ResumeSummary] = []
    for r in resumes:
        count = db.scalar(
            select(func.count(ResumeVersion.id)).where(
                ResumeVersion.resume_id == r.id
            )
        )
        latest = db.scalar(
            select(func.max(ResumeVersion.version_number)).where(
                ResumeVersion.resume_id == r.id
            )
        )
        out.append(
            ResumeSummary(
                id=r.id,
                kind=r.kind,
                name=r.name,
                version_count=count or 0,
                latest_version_number=latest,
            )
        )
    return out


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(resume_id: int, db: Session = Depends(get_db)) -> Resume:
    resume = _get_resume_or_404(db, resume_id)
    # versions relationship is ordered by version_number (see model)
    return resume


@router.post(
    "/{resume_id}/versions",
    response_model=ResumeVersionDetail,
    status_code=status.HTTP_201_CREATED,
)
def upload_version(
    resume_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ResumeVersion:
    resume = _get_resume_or_404(db, resume_id)

    filename = os.path.basename(file.filename or "")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Unsupported file type. Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    data = file.file.read()
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Uploaded file is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File exceeds 10 MB limit"
        )

    try:
        parsed_text = parse_resume(filename, data)
    except UnsupportedResumeType as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    next_version = (
        db.scalar(
            select(func.max(ResumeVersion.version_number)).where(
                ResumeVersion.resume_id == resume.id
            )
        )
        or 0
    ) + 1

    dest_dir = Path(settings.upload_dir) / "resumes" / str(resume.id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"v{next_version}__{filename}"
    dest_path.write_bytes(data)

    version = ResumeVersion(
        resume_id=resume.id,
        version_number=next_version,
        original_filename=filename,
        content_type=file.content_type,
        file_size=len(data),
        storage_path=str(dest_path),
        parsed_text=parsed_text,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.get("/versions/{version_id}", response_model=ResumeVersionDetail)
def get_version(version_id: int, db: Session = Depends(get_db)) -> ResumeVersion:
    version = db.get(ResumeVersion, version_id)
    if version is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume version not found")
    return version


@router.get("/versions/{version_id}/download")
def download_version(version_id: int, db: Session = Depends(get_db)) -> FileResponse:
    version = db.get(ResumeVersion, version_id)
    if version is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume version not found")
    if not os.path.exists(version.storage_path):
        raise HTTPException(status.HTTP_410_GONE, "Original file no longer available")
    return FileResponse(
        version.storage_path,
        filename=version.original_filename,
        media_type=version.content_type or "application/octet-stream",
    )
