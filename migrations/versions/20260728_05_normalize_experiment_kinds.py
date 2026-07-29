"""Normalize legacy mixed-case experiment kind values."""

from alembic import op

revision = "20260728_05"
down_revision = "20260728_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table_name in ("experiments", "experiment_runs"):
        op.execute(
            f"UPDATE {table_name} "
            "SET kind = lower(replace(replace(trim(kind), '-', '_'), ' ', '_'))"
        )


def downgrade() -> None:
    # Canonical lowercase values are also understood by earlier application versions.
    pass
