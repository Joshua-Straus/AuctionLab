"""Counterfactual weak-dominance experiment for second-price auctions."""

from __future__ import annotations

import random

import numpy as np
import pandas as pd


def _utility(
    valuation: float,
    bid: float,
    opponent_bids: list[float],
) -> float:
    """Return expected utility, sharing the allocation on an exact bid tie."""
    highest_opponent_bid = max(opponent_bids)
    if bid < highest_opponent_bid:
        return 0.0

    surplus = valuation - highest_opponent_bid
    if bid > highest_opponent_bid:
        return surplus

    tied_opponents = sum(bid == opponent_bid for opponent_bid in opponent_bids)
    return surplus / (tied_opponents + 1)


def _comparison_outcome(
    truthful_utility: float,
    alternative_utility: float,
) -> str:
    if np.isclose(truthful_utility, alternative_utility):
        return "tie"
    return "win" if truthful_utility > alternative_utility else "loss"


def run_vickrey_dominance_experiment(
    num_rounds: int = 5_000,
    bidder_count: int = 6,
    bid_spread: float = 20.0,
    bid_count: int = 9,
    low_value: float = 0.0,
    high_value: float = 100.0,
    seed: int = 42,
) -> dict:
    """Compare truthful utility with nearby bids under identical conditions."""
    if num_rounds <= 0:
        raise ValueError("num_rounds must be positive.")
    if bidder_count < 2:
        raise ValueError("bidder_count must be at least 2.")
    if bid_spread <= 0:
        raise ValueError("bid_spread must be positive.")
    if bid_count < 3 or bid_count % 2 == 0:
        raise ValueError("bid_count must be an odd number of at least 3.")
    if low_value > high_value:
        raise ValueError("Valuation range is invalid.")

    bid_deltas = np.linspace(-bid_spread, bid_spread, bid_count)
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []

    for round_id in range(1, num_rounds + 1):
        valuation = rng.uniform(low_value, high_value)
        opponent_bids = [
            rng.uniform(low_value, high_value)
            for _ in range(bidder_count - 1)
        ]
        highest_opponent_bid = max(opponent_bids)
        truthful_utility = _utility(valuation, valuation, opponent_bids)

        for bid_delta in bid_deltas:
            alternative_bid = max(0.0, valuation + float(bid_delta))
            alternative_utility = _utility(
                valuation,
                alternative_bid,
                opponent_bids,
            )
            rows.append(
                {
                    "round_id": round_id,
                    "auction_type": "second_price",
                    "valuation": valuation,
                    "highest_opponent_bid": highest_opponent_bid,
                    "bid_delta": float(bid_delta),
                    "alternative_bid": alternative_bid,
                    "truthful_utility": truthful_utility,
                    "alternative_utility": alternative_utility,
                    "utility_difference": truthful_utility
                    - alternative_utility,
                    "outcome": _comparison_outcome(
                        truthful_utility,
                        alternative_utility,
                    ),
                }
            )

    results = pd.DataFrame(rows)
    outcome_counts = (
        results.groupby(["bid_delta", "outcome"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["win", "tie", "loss"], fill_value=0)
        .reset_index()
        .rename(
            columns={
                "win": "truthful_wins",
                "tie": "ties",
                "loss": "truthful_losses",
            }
        )
    )
    utility_summary = (
        results.groupby("bid_delta", as_index=False)
        .agg(
            average_alternative_bid=("alternative_bid", "mean"),
            truthful_expected_utility=("truthful_utility", "mean"),
            alternative_expected_utility=("alternative_utility", "mean"),
            average_truthful_advantage=("utility_difference", "mean"),
        )
    )
    strategy_summary = outcome_counts.merge(utility_summary, on="bid_delta")
    strategy_summary["comparisons"] = num_rounds

    nontruthful = strategy_summary[~np.isclose(strategy_summary["bid_delta"], 0)]
    total_wins = int(nontruthful["truthful_wins"].sum())
    total_ties = int(nontruthful["ties"].sum())
    total_losses = int(nontruthful["truthful_losses"].sum())
    supports_proposition = total_losses == 0
    proposition = {
        "statement": (
            "Bidding your valuation weakly dominates nearby alternative bids "
            "in a second-price auction."
        ),
        "truthful_wins": total_wins,
        "ties": total_ties,
        "truthful_losses": total_losses,
        "total_comparisons": total_wins + total_ties + total_losses,
        "supports_proposition": supports_proposition,
        "interpretation": (
            "Truthful bidding never produced lower utility than a nearby bid "
            "under the same valuation and opponent bids."
            if supports_proposition
            else "At least one nearby bid produced higher utility; inspect the "
            "reported loss cases."
        ),
    }
    summary = {
        "num_rounds": num_rounds,
        "bidder_count": bidder_count,
        "bid_count": bid_count,
        "bid_spread": bid_spread,
        "low_value": low_value,
        "high_value": high_value,
    }
    return {
        "results": results,
        "agent_summary": strategy_summary.copy(),
        "strategy_summary": strategy_summary,
        "auction_summary": summary,
        "proposition": proposition,
    }
