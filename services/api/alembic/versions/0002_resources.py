"""resources, bookmarks and progress

Revision ID: 0002_resources
Revises: 0001_phase0_identity
Create Date: 2026-09-23
"""
import sqlalchemy as sa

from alembic import op

revision = "0002_resources"
down_revision = "0001_phase0_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "resources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("level", sa.String(length=40), nullable=False),
        sa.Column("group_name", sa.String(length=40), nullable=True),
        sa.Column("subject", sa.String(length=120), nullable=False),
        sa.Column("chapter", sa.String(length=160), nullable=True),
        sa.Column("resource_type", sa.String(length=60), nullable=False),
        sa.Column("attempt", sa.String(length=60), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=500), nullable=True),
        sa.Column("file_key", sa.String(length=500), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(length=120), nullable=True),
        sa.Column("official_icai", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_resources_active_filters", "resources", ["is_active", "level", "subject", "resource_type"])
    op.create_index("ix_resources_attempt_year", "resources", ["attempt", "year"])

    op.create_table(
        "resource_bookmarks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource_id", sa.Uuid(), sa.ForeignKey("resources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "resource_id", name="uq_resource_bookmarks_user_resource"),
    )
    op.create_table(
        "resource_progress",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource_id", sa.Uuid(), sa.ForeignKey("resources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_viewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "resource_id", name="uq_resource_progress_user_resource"),
    )


def downgrade() -> None:
    op.drop_table("resource_progress")
    op.drop_table("resource_bookmarks")
    op.drop_index("ix_resources_attempt_year", table_name="resources")
    op.drop_index("ix_resources_active_filters", table_name="resources")
    op.drop_table("resources")
