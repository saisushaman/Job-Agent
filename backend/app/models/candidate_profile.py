"""CandidateProfile — the single local user's profile (Phase 5).

Single-user, local-first: one row (created on first access). Facts here are provided by
the user; the AI never invents profile content.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.base import TimestampMixin


class CandidateProfile(Base, TimestampMixin):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    headline: Mapped[str | None] = mapped_column(String(255))
    years_experience: Mapped[float | None] = mapped_column(Float)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    languages: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["English"])
    current_location: Mapped[str | None] = mapped_column(String(120))
    current_country: Mapped[str | None] = mapped_column(String(120))
    preferred_regions: Mapped[list[str]] = mapped_column(
        JSON, default=lambda: ["USA", "EUROPE"]
    )
    needs_sponsorship: Mapped[bool] = mapped_column(Boolean, default=True)
    open_to_relocation: Mapped[bool] = mapped_column(Boolean, default=True)
    open_to_remote: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CandidateProfile id={self.id} name={self.full_name!r}>"

    def as_dict(self) -> dict[str, Any]:  # pragma: no cover - convenience
        return {
            "id": self.id,
            "full_name": self.full_name,
            "headline": self.headline,
            "years_experience": self.years_experience,
            "skills": self.skills,
            "languages": self.languages,
            "current_location": self.current_location,
            "current_country": self.current_country,
            "preferred_regions": self.preferred_regions,
            "needs_sponsorship": self.needs_sponsorship,
            "open_to_relocation": self.open_to_relocation,
            "open_to_remote": self.open_to_remote,
        }
