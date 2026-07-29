from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class ExperimentKind(str, enum.Enum):
    auction = "auction"
    first_price = "first_price"
    learning = "learning"
    vickrey = "vickrey"


class RunStatus(str, enum.Enum):
    completed = "completed"
    failed = "failed"


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    kind: Mapped[ExperimentKind] = mapped_column(
        Enum(
            ExperimentKind,
            native_enum=False,
            length=32,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        )
    )
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    runs: Mapped[list["ExperimentRun"]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("experiments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    kind: Mapped[ExperimentKind] = mapped_column(
        Enum(
            ExperimentKind,
            native_enum=False,
            length=32,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        )
    )
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus, native_enum=False))
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON)
    summary: Mapped[dict[str, Any]] = mapped_column(JSON)
    result: Mapped[dict[str, Any]] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
    experiment: Mapped[Experiment | None] = relationship(back_populates="runs")
