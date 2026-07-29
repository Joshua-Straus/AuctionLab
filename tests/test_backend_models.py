from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from backend.app.database import Base
from backend.app.models import Experiment, ExperimentKind, ExperimentRun


def test_experiment_kind_columns_have_safe_explicit_length():
    assert Experiment.__table__.c.kind.type.length == 32
    assert ExperimentRun.__table__.c.kind.type.length == 32


def test_experiment_kind_writes_canonical_value():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(
            Experiment(
                slug="canonical",
                name="Canonical",
                description="",
                kind=ExperimentKind.first_price,
                parameters={},
            )
        )
        session.commit()

    with engine.connect() as connection:
        stored_kind = connection.scalar(
            text("SELECT kind FROM experiments WHERE slug = 'canonical'")
        )

    assert stored_kind == "first_price"
