"""Candidate profile helpers (single-user, local-first)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile


def get_or_create_profile(db: Session) -> CandidateProfile:
    """Return the single profile row, creating a default one on first access."""
    profile = db.scalar(select(CandidateProfile).order_by(CandidateProfile.id).limit(1))
    if profile is None:
        profile = CandidateProfile(
            skills=[],
            languages=["English"],
            preferred_regions=["USA", "EUROPE"],
            needs_sponsorship=True,
            open_to_relocation=True,
            open_to_remote=True,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile
