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
        "slug": "balanced-double-auction",
        "name": "Balanced double auction",
        "description": "Eight truthful buyers trade with eight truthful sellers.",
        "kind": ExperimentKind.market,
        "parameters": {
            "num_rounds": 1000, "num_buyers": 8, "num_sellers": 8,
            "buyer_strategy": "truthful", "seller_strategy": "truthful",
            "buyer_alpha": 0.8, "seller_markup": 0.2,
            "buyer_value_low": 0.0, "buyer_value_high": 100.0,
            "seller_cost_low": 0.0, "seller_cost_high": 100.0, "seed": 42,
        },
    },
    {
        "slug": "strategic-double-auction",
        "name": "Strategic double auction",
        "description": "Shading buyers trade with markup sellers.",
        "kind": ExperimentKind.market,
        "parameters": {
            "num_rounds": 1000, "num_buyers": 8, "num_sellers": 8,
            "buyer_strategy": "shading", "seller_strategy": "markup",
            "buyer_alpha": 0.8, "seller_markup": 0.2,
            "buyer_value_low": 0.0, "buyer_value_high": 100.0,
            "seller_cost_low": 0.0, "seller_cost_high": 100.0, "seed": 42,
        },
    },
    {
        "slug": "bandit-learning",
        "name": "Bandit learning comparison",
        "description": "An epsilon-greedy bidder learns alongside fixed strategies.",
        "kind": ExperimentKind.learning,
        "parameters": {"num_rounds": 1000, "epsilon": 0.1, "seed": 42},
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
