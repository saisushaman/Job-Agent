"""resume system: resumes, resume_versions (+ seed default tracks)

Revision ID: 0002_resume_system
Revises: 0001_initial
Create Date: 2026-07-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.resume_tracks import DEFAULT_TRACKS

# revision identifiers, used by Alembic.
revision: str = "0002_resume_system"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    resumes = op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("kind", name="uq_resumes_kind"),
    )

    op.create_table(
        "resume_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("parsed_text", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_resume_versions_resume_id", "resume_versions", ["resume_id"]
    )

    # Seed the default resume tracks.
    op.bulk_insert(
        resumes,
        [{"kind": kind, "name": name} for kind, name in DEFAULT_TRACKS],
    )


def downgrade() -> None:
    op.drop_index("ix_resume_versions_resume_id", table_name="resume_versions")
    op.drop_table("resume_versions")
    op.drop_table("resumes")
