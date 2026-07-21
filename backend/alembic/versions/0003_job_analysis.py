"""job analysis

Revision ID: 0003_job_analysis
Revises: 0002_resume_system
Create Date: 2026-07-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_job_analysis"
down_revision: Union[str, None] = "0002_resume_system"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("region", sa.String(length=20), nullable=False),
        sa.Column("sponsorship_us", sa.String(length=40), nullable=True),
        sa.Column("visa_support_eu", sa.String(length=40), nullable=True),
        sa.Column("eligibility", sa.String(length=20), nullable=False),
        sa.Column(
            "citizenship_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "work_authorization_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("data", sa.JSON(), nullable=False),
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
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("job_id", name="uq_job_analyses_job_id"),
    )


def downgrade() -> None:
    op.drop_table("job_analyses")
