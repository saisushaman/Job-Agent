"""Prompt for email classification (Phase 9)."""

from __future__ import annotations

EMAIL_CLASSIFY_SYSTEM = (
    "You classify a single job-search-related email into exactly one category and give a "
    "calibrated confidence (0.0-1.0). Categories: APPLICATION_CONFIRMATION (acknowledges "
    "an application was received), RECRUITER_CONTACT (a recruiter reaching out), "
    "INTERVIEW (scheduling or inviting to an interview), ASSESSMENT (coding test / "
    "take-home / online assessment), REJECTION (application declined), OFFER (a job "
    "offer), FOLLOW_UP (a nudge or status follow-up), OTHER (newsletters, unrelated). "
    "Base the decision only on the email text. If genuinely unsure, lower the confidence. "
    "Output only valid JSON."
)


def build_email_classify_prompt(*, sender: str, subject: str, body: str) -> str:
    return (
        f"From: {sender}\nSubject: {subject}\n\nBody:\n{body[:4000]}\n\n"
        "Classify this email."
    )
