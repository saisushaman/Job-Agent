"""email messages

Revision ID: 0007_email_messages
Revises: 0006_tailored_documents
Create Date: 2026-07-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0007_email_messages"
down_revision: Union[str, None] = "0006_tailored_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "email_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("thread_id", sa.String(length=255), nullable=True),
        sa.Column("sender", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("sender_email", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("subject", sa.String(length=998), nullable=False, server_default=""),
        sa.Column("snippet", sa.Text(), nullable=False, server_default=""),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("classified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("category", sa.String(length=40), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("application_id", sa.Integer(), nullable=True),
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
            ["application_id"], ["applications.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint("external_id", name="uq_email_messages_external_id"),
    )
    op.create_index(
        "ix_email_messages_application_id", "email_messages", ["application_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_email_messages_application_id", table_name="email_messages")
    op.drop_table("email_messages")
