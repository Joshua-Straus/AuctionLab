from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Experiment, ExperimentKind


PREMADE_EXPERIMENTS: tuple[dict[str, Any], ...] = (
    {
        "slug": "first-price-mixed",
        "name": "First-price mixed strategies",
        "description": "Truthful, shading, and adaptive bidders compete together.",
        "kind": ExperimentKind.auction,
        "parameters": {
            "auction_type": "first_price", "num_rounds": 1000,
            "bidder_count": 6, "strategy": "mixed", "alpha": 0.8,
            "low_value": 0.0, "high_value": 100.0, "seed": 42,
        },
    },
    {
        "slug": "second-price-truthful",
        "name": "Second-price truthful benchmark",
        "description": "A truthful-bidding benchmark for second-price auctions.",
        "kind": ExperimentKind.auction,
        "parameters": {
            "auction_type": "second_price", "num_rounds": 1000,
            "bidder_count": 6, "strategy": "truthful", "alpha": 0.8,
            "low_value": 0.0, "high_value": 100.0, "seed": 42,
        },
    },
    {
        "slug": "bandit-learning",
        "name": "Bandit learning comparison",
        "description": "An epsilon-greedy bidder learns alongside fixed strategies.",
        "kind": ExperimentKind.learning,
        "parameters": {"num_rounds": 1000, "epsilon": 0.1, "seed": 42},
    },
    {
        "slug": "vickrey-dominant-strategy-test",
        "name": "Vickrey dominant-strategy test",
        "description": (
            "Compares truthful utility with an array of nearby bids under "
            "identical second-price auction conditions."
        ),
        "kind": ExperimentKind.vickrey,
        "parameters": {
            "num_rounds": 5000,
            "bidder_count": 6,
            "bid_spread": 20.0,
            "bid_count": 9,
            "low_value": 0.0,
            "high_value": 100.0,
            "seed": 42,
        },
    },
    {
        "slug": "sealed-bid-first-price-strategy-test",
        "name": "Sealed-bid first-price strategy test",
        "description": (
            "Compares average profit for truthful, random, shading, bandit, "
            "and equilibrium first-price bidders."
        ),
        "kind": ExperimentKind.first_price,
        "parameters": {
            "num_rounds": 5000,
            "agents_per_strategy": 3,
            "shading_alpha": 0.8,
            "epsilon": 0.1,
            "low_value": 0.0,
            "high_value": 100.0,
            "seed": 42,
        },
    },
    {
        "slug": "revenue-equality-test",
        "name": "Revenue Equality",
        "description": (
            "Compares seller revenue from equilibrium first-price and truthful "
            "second-price auctions under identical I.I.D. private values."
        ),
        "kind": ExperimentKind.revenue_equality,
        "parameters": {
            "num_rounds": 10000,
            "bidder_count": 16,
            "low_value": 0.0,
            "high_value": 100.0,
            "seed": 42,
        },
    },
)


def seed_experiments(session: Session) -> None:
    existing = set(session.scalars(select(Experiment.slug)).all())
    session.add_all(
        Experiment(**definition)
        for definition in PREMADE_EXPERIMENTS
        if definition["slug"] not in existing
    )
    session.commit()
