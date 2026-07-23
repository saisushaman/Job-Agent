"""Resume tailoring service (Phase 8): pick best resume, tailor via Qwen3, gen docs."""

from __future__ import annotations

import io

from docx import Document
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.base import AIProvider
from app.ai.prompts.tailoring import TAILORING_SYSTEM, build_tailoring_prompt
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job
from app.models.resume import ResumeVersion
from app.services.matching import cosine
from app.schemas.tailoring import TailorResult


def pick_best_resume_version(
    provider: AIProvider, db: Session, job: Job
) -> ResumeVersion | None:
    """Choose the latest version of each resume track whose text best matches the job."""
    # latest version_number per resume track
    subq = (
        select(
            ResumeVersion.resume_id,
            func.max(ResumeVersion.version_number).label("maxv"),
        )
        .group_by(ResumeVersion.resume_id)
        .subquery()
    )
    latest = db.scalars(
        select(ResumeVersion).join(
            subq,
            (ResumeVersion.resume_id == subq.c.resume_id)
            & (ResumeVersion.version_number == subq.c.maxv),
        )
    ).all()
    if not latest:
        return None
    if len(latest) == 1:
        return latest[0]

    job_text = f"{job.title} {job.description or ''}"[:2000]
    job_vec = provider.embed(job_text)
    best: ResumeVersion | None = None
    best_sim = -2.0
    for v in latest:
        sim = cosine(job_vec, provider.embed((v.parsed_text or "")[:2000]))
        if sim > best_sim:
            best_sim, best = sim, v
    return best


def _profile_summary(profile: CandidateProfile | None) -> str:
    if profile is None:
        return "(no profile provided)"
    parts = [
        profile.headline or "",
        f"Experience: {profile.years_experience} years"
        if profile.years_experience is not None
        else "",
        f"Skills: {', '.join(profile.skills or [])}",
        f"Languages: {', '.join(profile.languages or [])}",
    ]
    return "\n".join(p for p in parts if p)


def tailor(
    provider: AIProvider,
    *,
    resume_version: ResumeVersion,
    profile: CandidateProfile | None,
    job: Job,
    questions: list[str],
) -> TailorResult:
    prompt = build_tailoring_prompt(
        resume_text=resume_version.parsed_text or "",
        profile_summary=_profile_summary(profile),
        job_title=job.title,
        company=job.company,
        job_description=job.description or "",
        questions=questions,
    )
    return provider.generate_json(prompt, TailorResult, system=TAILORING_SYSTEM)


DOCX_MEDIA = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def text_to_docx_bytes(text: str) -> bytes:
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
