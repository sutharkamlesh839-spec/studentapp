"""videos, opportunities, official updates and paper evaluation

Revision ID: 0004_operations_content
Revises: 0003_learning_domains
Create Date: 2026-09-25
"""
import sqlalchemy as sa

from alembic import op

revision = "0004_operations_content"
down_revision = "0003_learning_domains"
branch_labels = None
depends_on = None


def uuid_column(name: str, *, primary_key: bool = False, nullable: bool = False):
    return sa.Column(name, sa.Uuid(), primary_key=primary_key, nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "video_lessons",
        uuid_column("id", primary_key=True),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("level", sa.String(40), nullable=False),
        sa.Column("subject", sa.String(120), nullable=False),
        sa.Column("chapter", sa.String(160), nullable=True),
        sa.Column("video_url", sa.String(1000), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_video_lessons_level_subject", "video_lessons", ["level", "subject", "is_active"])

    op.create_table(
        "opportunities",
        uuid_column("id", primary_key=True),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("organisation", sa.String(180), nullable=True),
        sa.Column("location", sa.String(160), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("application_url", sa.String(1000), nullable=True),
        sa.Column("target_level", sa.String(40), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_opportunities_kind_active", "opportunities", ["kind", "is_active", "created_at"])

    op.create_table(
        "official_updates",
        uuid_column("id", primary_key=True),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("source_url", sa.String(1000), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
    )
    op.create_index("ix_official_updates_published", "official_updates", ["published_at", "is_active"])

    op.create_table(
        "paper_submissions",
        uuid_column("id", primary_key=True),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_to", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("subject", sa.String(120), nullable=False),
        sa.Column("file_key", sa.String(500), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="submitted"),
        sa.Column("marks", sa.Float(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_paper_submissions_status_assigned", "paper_submissions", ["status", "assigned_to", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_paper_submissions_status_assigned", table_name="paper_submissions")
    op.drop_table("paper_submissions")
    op.drop_index("ix_official_updates_published", table_name="official_updates")
    op.drop_table("official_updates")
    op.drop_index("ix_opportunities_kind_active", table_name="opportunities")
    op.drop_table("opportunities")
    op.drop_index("ix_video_lessons_level_subject", table_name="video_lessons")
    op.drop_table("video_lessons")
