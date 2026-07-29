"""Add the dedicated Vickrey experiment kind."""

revision = "20260728_03"
down_revision = "20260728_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Experiment kinds are stored as strings; seed startup inserts the definition.
    pass


def downgrade() -> None:
    pass
