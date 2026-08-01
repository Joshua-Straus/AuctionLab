from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from backend.app.models import Experiment, ExperimentKind, ExperimentRun, RunStatus
from backend.app.schemas import (
    AuctionRunRequest,
    FirstPriceStrategyRunRequest,
    LearningRunRequest,
    RevenueEqualityRunRequest,
    VickreyRunRequest,
)
from auction_sim.first_price_research import run_first_price_strategy_experiment
from auction_sim.revenue_equality import run_revenue_equality_experiment
from auction_sim.vickrey import run_vickrey_dominance_experiment
from dashboard_logic import (
    run_auction_dashboard,
    run_learning_dashboard,
)


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return frame.where(pd.notna(frame), None).to_dict(orient="records")


def execute(kind: ExperimentKind, parameters: dict[str, Any]) -> dict[str, Any]:
    if kind == ExperimentKind.auction:
        request = AuctionRunRequest.model_validate(parameters)
        raw = run_auction_dashboard(**request.model_dump())
        return jsonable_encoder({
            "results": _records(raw["results"]),
            "agent_summary": _records(raw["agent_summary"]),
            "summary": raw["auction_summary"],
        })
    if kind == ExperimentKind.vickrey:
        request = VickreyRunRequest.model_validate(parameters)
        raw = run_vickrey_dominance_experiment(**request.model_dump())
        return jsonable_encoder({
            "results": _records(raw["results"]),
            "agent_summary": _records(raw["agent_summary"]),
            "strategy_summary": _records(raw["strategy_summary"]),
            "summary": raw["auction_summary"],
            "proposition": raw["proposition"],
        })
    if kind == ExperimentKind.first_price:
        request = FirstPriceStrategyRunRequest.model_validate(parameters)
        raw = run_first_price_strategy_experiment(**request.model_dump())
        return jsonable_encoder({
            "results": _records(raw["results"]),
            "agent_summary": _records(raw["agent_summary"]),
            "strategy_summary": _records(raw["strategy_summary"]),
            "summary": raw["auction_summary"],
            "comparison": raw["comparison"],
        })
    if kind == ExperimentKind.revenue_equality:
        request = RevenueEqualityRunRequest.model_validate(parameters)
        raw = run_revenue_equality_experiment(**request.model_dump())
        revenue_records = _records(raw["revenue_by_trial"])
        return jsonable_encoder({
            "results": revenue_records,
            "agent_summary": [],
            "revenue_by_trial": revenue_records,
            "format_summary": _records(raw["format_summary"]),
            "summary": raw["summary"],
            "comparison": raw["comparison"],
        })
    request = LearningRunRequest.model_validate(parameters)
    raw = run_learning_dashboard(**request.model_dump())
    return jsonable_encoder({
        "results": _records(raw["results"]),
        "agent_summary": _records(raw["agent_summary"]),
        "summary": raw["auction_summary"],
        "cumulative_profit": _records(raw["cumulative_profit"]),
        "action_summary": _records(raw["action_summary"]),
        "action_history": _records(raw["action_history"]),
    })


def execute_and_store(
    session: Session,
    kind: ExperimentKind,
    parameters: dict[str, Any],
    experiment: Experiment | None = None,
) -> dict[str, Any]:
    try:
        result = execute(kind, parameters)
        run = ExperimentRun(
            experiment=experiment, kind=kind, status=RunStatus.completed,
            parameters=parameters, summary=result["summary"], result=result,
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        return {**result, "run_id": run.id}
    except Exception as error:
        session.rollback()
        session.add(
            ExperimentRun(
                experiment=experiment, kind=kind, status=RunStatus.failed,
                parameters=parameters, summary={}, result={}, error=str(error),
            )
        )
        session.commit()
        raise
