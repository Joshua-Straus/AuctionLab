"""Create experiment definition and run tables."""

from alembic import op
import sqlalchemy as sa

revision = "20260724_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "experiments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum("auction", "market", "learning", name="experimentkind", native_enum=False),
            nullable=False,
        ),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_experiments_slug", "experiments", ["slug"], unique=True)
    op.create_table(
        "experiment_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_id", sa.Uuid(), nullable=True),
        sa.Column(
            "kind",
            sa.Enum("auction", "market", "learning", name="experimentkind", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("completed", "failed", name="runstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("summary", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_experiment_runs_experiment_id", "experiment_runs", ["experiment_id"])


def downgrade() -> None:
    op.drop_index("ix_experiment_runs_experiment_id", table_name="experiment_runs")
    op.drop_table("experiment_runs")
    op.drop_index("ix_experiments_slug", table_name="experiments")
    op.drop_table("experiments")
