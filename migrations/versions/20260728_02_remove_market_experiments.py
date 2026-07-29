"""Remove market experiment data from existing databases."""

from alembic import op

revision = "20260728_02"
down_revision = "20260724_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM experiment_runs WHERE kind = 'market'")
    op.execute("DELETE FROM experiments WHERE kind = 'market'")


def downgrade() -> None:
    # Removed market definitions and run results cannot be reconstructed.
    pass
