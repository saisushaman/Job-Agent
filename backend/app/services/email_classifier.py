"""Email classification + matching helpers (Phase 9)."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.base import AIProvider
from app.ai.prompts.email import EMAIL_CLASSIFY_SYSTEM, build_email_classify_prompt
from app.models.application import Application
from app.models.email_message import EmailMessage
from app.models.job import Job
from app.schemas.email import EmailClassificationResult

# Categories that imply a concrete pipeline status. Applied only for matched emails
# above the confidence threshold. OTHER / FOLLOW_UP intentionally omitted.
CATEGORY_TO_STATUS: dict[str, str] = {
    "APPLICATION_CONFIRMATION": "APPLIED",
    "RECRUITER_CONTACT": "RESPONSE_RECEIVED",
    "INTERVIEW": "INTERVIEW",
    "ASSESSMENT": "INTERVIEW",
    "REJECTION": "REJECTED",
    "OFFER": "OFFER",
}


def classify_email(provider: AIProvider, email: EmailMessage) -> EmailClassificationResult:
    prompt = build_email_classify_prompt(
        sender=f"{email.sender} <{email.sender_email}>",
        subject=email.subject,
        body=email.body or email.snippet,
    )
    return provider.generate_json(
        prompt, EmailClassificationResult, system=EMAIL_CLASSIFY_SYSTEM
    )


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def match_application(db: Session, email: EmailMessage) -> Application | None:
    """Match an email to an application by the job's company appearing in the email."""
    haystack = _norm(f"{email.sender} {email.sender_email} {email.subject} {email.body}")
    if not haystack:
        return None
    apps = db.scalars(select(Application)).all()
    best: Application | None = None
    best_len = 0
    for app in apps:
        company = _norm(app.job.company)
        if company and company in haystack and len(company) > best_len:
            best, best_len = app, len(company)
    return best
