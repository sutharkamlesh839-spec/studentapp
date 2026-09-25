"""learning, tests, queries, notifications and analytics data

Revision ID: 0003_learning_domains
Revises: 0002_resources
Create Date: 2026-09-25
"""
import sqlalchemy as sa

from alembic import op

revision = "0003_learning_domains"
down_revision = "0002_resources"
branch_labels = None
depends_on = None


def uuid_column(name: str, *, primary_key: bool = False, nullable: bool = False):
    return sa.Column(name, sa.Uuid(), primary_key=primary_key, nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "mcq_questions",
        uuid_column("id", primary_key=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("correct_option", sa.Integer(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("subject", sa.String(120), nullable=False),
        sa.Column("chapter", sa.String(160), nullable=True),
        sa.Column("difficulty", sa.String(30), nullable=False, server_default="medium"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_mcq_questions_active_subject", "mcq_questions", ["is_active", "subject", "chapter"])

    op.create_table(
        "mcq_responses",
        uuid_column("id", primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Uuid(), sa.ForeignKey("mcq_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("selected_option", sa.Integer(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_mcq_responses_user_created", "mcq_responses", ["user_id", "created_at"])

    op.create_table(
        "syllabus_items",
        uuid_column("id", primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject", sa.String(120), nullable=False),
        sa.Column("chapter", sa.String(160), nullable=False),
        sa.Column("total_topics", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("completed_topics", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(30), nullable=False, server_default="not_started"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "subject", "chapter", name="uq_syllabus_user_subject_chapter"),
    )

    op.create_table(
        "study_plan_tasks",
        uuid_column("id", primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("subject", sa.String(120), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_study_plan_tasks_user_due", "study_plan_tasks", ["user_id", "due_date"])

    op.create_table(
        "revision_items",
        uuid_column("id", primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("subject", sa.String(120), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="due"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_revision_items_user_due", "revision_items", ["user_id", "due_at"])

    op.create_table(
        "practice_tests",
        uuid_column("id", primary_key=True),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("marks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("question_ids", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="open"),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_practice_tests_status_created", "practice_tests", ["status", "created_at"])

    op.create_table(
        "test_attempts",
        uuid_column("id", primary_key=True),
        sa.Column("test_id", sa.Uuid(), sa.ForeignKey("practice_tests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_test_attempts_user_submitted", "test_attempts", ["user_id", "submitted_at"])

    op.create_table(
        "support_queries",
        uuid_column("id", primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_to", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("subject", sa.String(120), nullable=False),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_support_queries_status_created", "support_queries", ["status", "created_at"])

    op.create_table(
        "notifications",
        uuid_column("id", primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False, server_default="general"),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_user_read_created", "notifications", ["user_id", "read_at", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_notifications_user_read_created", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_support_queries_status_created", table_name="support_queries")
    op.drop_table("support_queries")
    op.drop_index("ix_test_attempts_user_submitted", table_name="test_attempts")
    op.drop_table("test_attempts")
    op.drop_index("ix_practice_tests_status_created", table_name="practice_tests")
    op.drop_table("practice_tests")
    op.drop_index("ix_revision_items_user_due", table_name="revision_items")
    op.drop_table("revision_items")
    op.drop_index("ix_study_plan_tasks_user_due", table_name="study_plan_tasks")
    op.drop_table("study_plan_tasks")
    op.drop_table("syllabus_items")
    op.drop_index("ix_mcq_responses_user_created", table_name="mcq_responses")
    op.drop_table("mcq_responses")
    op.drop_index("ix_mcq_questions_active_subject", table_name="mcq_questions")
    op.drop_table("mcq_questions")
