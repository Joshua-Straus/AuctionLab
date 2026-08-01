"""Add the dedicated revenue-equality experiment kind."""

revision = "20260801_07"
down_revision = "20260728_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Experiment kinds use the existing VARCHAR(32) columns.
    pass


def downgrade() -> None:
    pass
