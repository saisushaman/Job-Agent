"""Application model — the candidate's application against a Job.

Phase 1 stores a minimal record. The full status lifecycle, recruiter info, audit
events, etc. arrive in Phase 7. ``status`` is a plain string here (validated in the
service layer later) to keep migrations simple across SQLite and Postgres.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.job import Job

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

    job: Mapped["Job"] = relationship(back_populates="applications")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Application id={self.id} job_id={self.job_id} status={self.status!r}>"
