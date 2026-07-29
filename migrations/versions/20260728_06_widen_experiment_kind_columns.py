"""Widen experiment kind columns for the first_price value."""

from alembic import op
import sqlalchemy as sa

revision = "20260728_06"
down_revision = "20260728_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "experiments",
        "kind",
        existing_type=sa.String(length=8),
        type_=sa.String(length=32),
        existing_nullable=False,
    )
    op.alter_column(
        "experiment_runs",
        "kind",
        existing_type=sa.String(length=8),
        type_=sa.String(length=32),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "experiment_runs",
        "kind",
        existing_type=sa.String(length=32),
        type_=sa.String(length=8),
        existing_nullable=False,
    )
    op.alter_column(
        "experiments",
        "kind",
        existing_type=sa.String(length=32),
        type_=sa.String(length=8),
        existing_nullable=False,
    )
