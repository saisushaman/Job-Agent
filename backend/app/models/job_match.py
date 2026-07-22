"""JobMatch — computed match of a Job against the candidate profile (Phase 5)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.job import Job


class JobMatch(Base, TimestampMixin):
    __tablename__ = "job_matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(20), nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    job: Mapped["Job"] = relationship(back_populates="match")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<JobMatch job_id={self.job_id} overall={self.overall_score} "
            f"rec={self.recommendation}>"
        )
