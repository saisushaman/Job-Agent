"""application tracker: extend applications + application_events

Revision ID: 0005_application_tracker
Revises: 0004_matching
Create Date: 2026-07-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_application_tracker"
down_revision: Union[str, None] = "0004_matching"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("applications") as batch:
        batch.add_column(sa.Column("external_application_id", sa.String(255), nullable=True))
        batch.add_column(sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("resume_version_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("cover_letter", sa.Text(), nullable=True))
        batch.add_column(sa.Column("recruiter_name", sa.String(255), nullable=True))
        batch.add_column(sa.Column("recruiter_email", sa.String(255), nullable=True))
        batch.add_column(sa.Column("recruiter_notes", sa.Text(), nullable=True))
        batch.add_column(sa.Column("interview_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("rejection_reason", sa.Text(), nullable=True))
        batch.add_column(sa.Column("offer_details", sa.Text(), nullable=True))
        batch.add_column(sa.Column("offer_salary", sa.Float(), nullable=True))
        batch.create_foreign_key(
            "fk_applications_resume_version_id",
            "resume_versions",
            ["resume_version_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_table(
        "application_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("from_status", sa.String(length=50), nullable=True),
        sa.Column("to_status", sa.String(length=50), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
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
    )
    op.create_index(
        "ix_application_events_application_id",
        "application_events",
        ["application_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_application_events_application_id", table_name="application_events"
    )
    op.drop_table("application_events")
    with op.batch_alter_table("applications") as batch:
        batch.drop_constraint("fk_applications_resume_version_id", type_="foreignkey")
        for col in (
            "offer_salary",
            "offer_details",
            "rejection_reason",
            "interview_at",
            "recruiter_notes",
            "recruiter_email",
            "recruiter_name",
            "cover_letter",
            "resume_version_id",
            "applied_at",
            "external_application_id",
        ):
            batch.drop_column(col)
