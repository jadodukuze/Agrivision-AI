"""Create initial AgriVision AI relational schema.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=190), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), server_default="farmer", nullable=False),
        sa.Column("preferred_language", sa.String(length=5), server_default="en", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "crop_cases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("crop_name", sa.String(length=80), nullable=False),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_path", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="submitted", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["farmer_id"], ["users.id"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crop_cases_farmer_id", "crop_cases", ["farmer_id"], unique=False)
    op.create_index("ix_crop_cases_id", "crop_cases", ["id"], unique=False)

    op.create_table(
        "expert_reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("expert_id", sa.Integer(), nullable=False),
        sa.Column("assessment", sa.Text(), nullable=False),
        sa.Column("recommended_next_steps", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["crop_cases.id"], ondelete="CASCADE", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["expert_id"], ["users.id"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_expert_reviews_case_id", "expert_reviews", ["case_id"], unique=False)
    op.create_index("ix_expert_reviews_id", "expert_reviews", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_expert_reviews_id", table_name="expert_reviews")
    op.drop_index("ix_expert_reviews_case_id", table_name="expert_reviews")
    op.drop_table("expert_reviews")
    op.drop_index("ix_crop_cases_id", table_name="crop_cases")
    op.drop_index("ix_crop_cases_farmer_id", table_name="crop_cases")
    op.drop_table("crop_cases")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
