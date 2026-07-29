"""Add the dedicated first-price strategy experiment kind."""

revision = "20260728_04"
down_revision = "20260728_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Experiment kinds are stored as strings; seed startup inserts the definition.
    pass


def downgrade() -> None:
    pass
