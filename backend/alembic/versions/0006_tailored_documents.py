"""tailored documents

Revision ID: 0006_tailored_documents
Revises: 0005_application_tracker
Create Date: 2026-07-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006_tailored_documents"
down_revision: Union[str, None] = "0005_application_tracker"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tailored_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("source_resume_version_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="DRAFT"),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tailored_resume", sa.Text(), nullable=False, server_default=""),
        sa.Column("cover_letter", sa.Text(), nullable=False, server_default=""),
        sa.Column("draft_answers", sa.JSON(), nullable=False),
        sa.Column("changes_summary", sa.JSON(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["application_id"], ["applications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["source_resume_version_id"], ["resume_versions.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint("application_id", name="uq_tailored_documents_application_id"),
    )


def downgrade() -> None:
    op.drop_table("tailored_documents")
