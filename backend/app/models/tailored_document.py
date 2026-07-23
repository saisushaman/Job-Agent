"""TailoredDocument — AI-assisted application prep for one application (Phase 8).

Holds the tailored resume, cover letter, and draft answers. Always starts as a DRAFT
requiring explicit user approval before it is considered saved/final.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.application import Application

STATUS_DRAFT = "DRAFT"
STATUS_APPROVED = "APPROVED"


class TailoredDocument(Base, TimestampMixin):
    __tablename__ = "tailored_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    source_resume_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("resume_versions.id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_DRAFT)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tailored_resume: Mapped[str] = mapped_column(Text, default="")
    cover_letter: Mapped[str] = mapped_column(Text, default="")
    draft_answers: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    changes_summary: Mapped[list[str]] = mapped_column(JSON, default=list)

    application: Mapped["Application"] = relationship()

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<TailoredDocument app={self.application_id} status={self.status}>"
        )
