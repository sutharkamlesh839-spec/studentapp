"""annotated files for faculty paper review

Revision ID: 0005_paper_annotations
Revises: 0004_operations_content
Create Date: 2026-09-25
"""
import sqlalchemy as sa

from alembic import op

revision = "0005_paper_annotations"
down_revision = "0004_operations_content"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("paper_submissions", sa.Column("annotated_file_key", sa.String(500), nullable=True))
    op.add_column("paper_submissions", sa.Column("annotated_file_name", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("paper_submissions", "annotated_file_name")
    op.drop_column("paper_submissions", "annotated_file_key")
