"""Application model — the candidate's application against a Job (Phase 1 + Phase 7).

Phase 7 fleshes out the full lifecycle: dates, resume version used, cover letter,
recruiter info, interview/rejection/offer details, plus an audit trail (ApplicationEvent).
``status`` is a plain string validated in the service layer against APPLICATION_STATUSES.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.resume import ResumeVersion

DEFAULT_STATUS = "DISCOVERED"


class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=DEFAULT_STATUS
    )
    notes: Mapped[str | None] = mapped_column(Text)

    # Phase 7 lifecycle fields
    external_application_id: Mapped[str | None] = mapped_column(String(255))
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resume_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("resume_versions.id", ondelete="SET NULL")
    )
    cover_letter: Mapped[str | None] = mapped_column(Text)
    recruiter_name: Mapped[str | None] = mapped_column(String(255))
    recruiter_email: Mapped[str | None] = mapped_column(String(255))
    recruiter_notes: Mapped[str | None] = mapped_column(Text)
    interview_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    offer_details: Mapped[str | None] = mapped_column(Text)
    offer_salary: Mapped[float | None] = mapped_column(Float)

    job: Mapped["Job"] = relationship(back_populates="applications")
    resume_version: Mapped["ResumeVersion | None"] = relationship()
    events: Mapped[list["ApplicationEvent"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationEvent.id",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Application id={self.id} job_id={self.job_id} status={self.status!r}>"


class ApplicationEvent(Base, TimestampMixin):
    __tablename__ = "application_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(50))
    to_status: Mapped[str | None] = mapped_column(String(50))
    message: Mapped[str | None] = mapped_column(Text)

    application: Mapped["Application"] = relationship(back_populates="events")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ApplicationEvent id={self.id} type={self.event_type}>"
