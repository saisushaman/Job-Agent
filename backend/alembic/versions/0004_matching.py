"""matching: candidate_profiles, job_matches

Revision ID: 0004_matching
Revises: 0003_job_analysis
Create Date: 2026-07-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_matching"
down_revision: Union[str, None] = "0003_job_analysis"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "candidate_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("headline", sa.String(length=255), nullable=True),
        sa.Column("years_experience", sa.Float(), nullable=True),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("languages", sa.JSON(), nullable=False),
        sa.Column("current_location", sa.String(length=120), nullable=True),
        sa.Column("current_country", sa.String(length=120), nullable=True),
        sa.Column("preferred_regions", sa.JSON(), nullable=False),
        sa.Column(
            "needs_sponsorship", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "open_to_relocation", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "open_to_remote", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
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
    )

    op.create_table(
        "job_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("recommendation", sa.String(length=20), nullable=False),
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
        sa.UniqueConstraint("job_id", name="uq_job_matches_job_id"),
    )


def downgrade() -> None:
    op.drop_table("job_matches")
    op.drop_table("candidate_profiles")
