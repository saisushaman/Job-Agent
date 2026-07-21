"""JobAnalysis model — one-to-one with a Job (Phase 4).

Common query fields are stored as columns (for Phase 6 filtering); the full structured
result is stored as JSON in ``data``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.job import Job


class JobAnalysis(Base, TimestampMixin):
    __tablename__ = "job_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    region: Mapped[str] = mapped_column(String(20), nullable=False)
    sponsorship_us: Mapped[str | None] = mapped_column(String(40))
    visa_support_eu: Mapped[str | None] = mapped_column(String(40))
    eligibility: Mapped[str] = mapped_column(String(20), nullable=False)
    citizenship_required: Mapped[bool] = mapped_column(Boolean, default=False)
    work_authorization_required: Mapped[bool] = mapped_column(Boolean, default=False)
    summary: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    job: Mapped["Job"] = relationship(back_populates="analysis")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<JobAnalysis job_id={self.job_id} region={self.region} "
            f"eligibility={self.eligibility}>"
        )
