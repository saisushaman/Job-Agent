"""Resume models.

A ``Resume`` is a named track (Master, Software Engineer, ...). Each file upload to a
track creates a new ``ResumeVersion`` — that's the version history. Phase 3 only stores
and parses resumes; no AI tailoring happens here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    pass


class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable machine key for the track, e.g. "MASTER", "SOFTWARE_ENGINEER".
    kind: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    # Human-friendly display name, e.g. "Software Engineer".
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    versions: Mapped[list["ResumeVersion"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="ResumeVersion.version_number",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Resume id={self.id} kind={self.kind!r}>"


class ResumeVersion(Base, TimestampMixin):
    __tablename__ = "resume_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120))
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    parsed_text: Mapped[str] = mapped_column(Text, nullable=False, default="")

    resume: Mapped["Resume"] = relationship(back_populates="versions")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ResumeVersion id={self.id} resume_id={self.resume_id} "
            f"v={self.version_number}>"
        )
