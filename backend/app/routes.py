from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Experiment, ExperimentKind, ExperimentRun
from backend.app.schemas import (
    AuctionRunRequest,
    ExperimentResponse,
    ExperimentRunRequest,
    ExperimentRunResponse,
    FirstPriceStrategyRunRequest,
    LearningRunRequest,
    RevenueEqualityRunRequest,
    SimulationResponse,
    VickreyRunRequest,
)
from backend.app.services import execute_and_store

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@router.post("/simulations/auctions", response_model=SimulationResponse)
def run_auction(request: AuctionRunRequest, db: Session = Depends(get_db)):
    return execute_and_store(db, ExperimentKind.auction, request.model_dump())


@router.post("/simulations/learning", response_model=SimulationResponse)
def run_learning(request: LearningRunRequest, db: Session = Depends(get_db)):
    return execute_and_store(db, ExperimentKind.learning, request.model_dump())


@router.post("/simulations/vickrey", response_model=SimulationResponse)
def run_vickrey(request: VickreyRunRequest, db: Session = Depends(get_db)):
    return execute_and_store(db, ExperimentKind.vickrey, request.model_dump())


@router.post(
    "/simulations/first-price-strategies",
    response_model=SimulationResponse,
)
def run_first_price_strategies(
    request: FirstPriceStrategyRunRequest,
    db: Session = Depends(get_db),
):
    return execute_and_store(db, ExperimentKind.first_price, request.model_dump())


@router.post("/simulations/revenue-equality", response_model=SimulationResponse)
def run_revenue_equality(
    request: RevenueEqualityRunRequest,
    db: Session = Depends(get_db),
):
    return execute_and_store(
        db,
        ExperimentKind.revenue_equality,
        request.model_dump(),
    )


@router.get("/experiments", response_model=list[ExperimentResponse])
def list_experiments(db: Session = Depends(get_db)):
    return db.scalars(select(Experiment).order_by(Experiment.name)).all()


@router.get("/experiments/{slug}", response_model=ExperimentResponse)
def get_experiment(slug: str, db: Session = Depends(get_db)):
    experiment = db.scalar(select(Experiment).where(Experiment.slug == slug))
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.post("/experiments/{slug}/run", response_model=SimulationResponse)
def run_experiment(
    slug: str, request: ExperimentRunRequest, db: Session = Depends(get_db)
):
    experiment = db.scalar(select(Experiment).where(Experiment.slug == slug))
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    parameters = {**experiment.parameters, **request.overrides}
    try:
        return execute_and_store(db, experiment.kind, parameters, experiment)
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors()) from error


@router.get("/runs/{run_id}", response_model=ExperimentRunResponse)
def get_run(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = db.get(ExperimentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
