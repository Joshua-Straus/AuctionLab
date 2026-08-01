"""Paired Monte Carlo test of revenue equivalence across auction formats."""

from __future__ import annotations

import math

import pandas as pd

from auction_sim.agents import EquilibriumFirstPriceAgent, TruthfulAgent
from auction_sim.config import ExperimentConfig
from auction_sim.experiments import run_experiment


def run_revenue_equality_experiment(
    num_rounds: int = 10_000,
    bidder_count: int = 16,
    low_value: float = 0.0,
    high_value: float = 100.0,
    seed: int = 42,
) -> dict:
    """Compare seller revenue under equilibrium first- and second-price bids."""
    if num_rounds <= 0:
        raise ValueError("num_rounds must be positive.")
    if bidder_count < 2:
        raise ValueError("bidder_count must be at least 2.")
    if low_value > high_value:
        raise ValueError("Valuation range is invalid.")

    config_values = {
        "num_rounds": num_rounds,
        "low_value": low_value,
        "high_value": high_value,
        "seed": seed,
    }
    first_price_results, _, first_price_summary = run_experiment(
        config=ExperimentConfig(auction_type="first_price", **config_values),
        agents=[
            EquilibriumFirstPriceAgent(agent_id=f"equilibrium_{index}")
            for index in range(bidder_count)
        ],
    )
    second_price_results, _, second_price_summary = run_experiment(
        config=ExperimentConfig(auction_type="second_price", **config_values),
        agents=[
            TruthfulAgent(agent_id=f"truthful_{index}")
            for index in range(bidder_count)
        ],
    )

    first_revenue = (
        first_price_results.drop_duplicates("round_id")
        [["round_id", "seller_revenue"]]
        .assign(auction_format="First price")
    )
    second_revenue = (
        second_price_results.drop_duplicates("round_id")
        [["round_id", "seller_revenue"]]
        .assign(auction_format="Second price")
    )
    revenue_by_trial = pd.concat(
        [first_revenue, second_revenue], ignore_index=True
    )[["round_id", "auction_format", "seller_revenue"]]
    format_summary = (
        revenue_by_trial.groupby("auction_format", as_index=False)
        .agg(
            average_seller_revenue=("seller_revenue", "mean"),
            revenue_std_dev=("seller_revenue", "std"),
            total_seller_revenue=("seller_revenue", "sum"),
            minimum_revenue=("seller_revenue", "min"),
            maximum_revenue=("seller_revenue", "max"),
        )
    )
    format_summary["standard_error"] = (
        format_summary["revenue_std_dev"] / math.sqrt(num_rounds)
    )

    paired = first_revenue.merge(
        second_revenue,
        on="round_id",
        suffixes=("_first_price", "_second_price"),
    )
    differences = (
        paired["seller_revenue_first_price"]
        - paired["seller_revenue_second_price"]
    )
    average_difference = float(differences.mean())
    difference_standard_error = float(differences.std() / math.sqrt(num_rounds))
    confidence_low = average_difference - 1.96 * difference_standard_error
    confidence_high = average_difference + 1.96 * difference_standard_error
    averages = format_summary.set_index("auction_format")[
        "average_seller_revenue"
    ]
    first_average = float(averages["First price"])
    second_average = float(averages["Second price"])
    relative_difference = (
        average_difference / second_average * 100.0
        if second_average != 0
        else 0.0
    )
    consistent = confidence_low <= 0.0 <= confidence_high
    theoretical_revenue = low_value + (
        (high_value - low_value) * (bidder_count - 1) / (bidder_count + 1)
    )
    comparison = {
        "question": (
            "Do equilibrium first-price and truthful second-price auctions "
            "produce equal expected seller revenue?"
        ),
        "first_price_average_revenue": first_average,
        "second_price_average_revenue": second_average,
        "average_revenue_difference": average_difference,
        "relative_difference_percent": relative_difference,
        "difference_standard_error": difference_standard_error,
        "difference_95_ci_low": confidence_low,
        "difference_95_ci_high": confidence_high,
        "theoretical_expected_revenue": theoretical_revenue,
        "consistent_with_revenue_equality": consistent,
        "interpretation": (
            "The paired 95% confidence interval contains zero, so the simulation "
            "is consistent with revenue equality."
            if consistent
            else "The paired 95% confidence interval excludes zero; increase the "
            "trial count or inspect the maintained assumptions."
        ),
    }
    return {
        "revenue_by_trial": revenue_by_trial,
        "format_summary": format_summary,
        "comparison": comparison,
        "summary": {
            "num_rounds": num_rounds,
            "bidder_count": bidder_count,
            "low_value": low_value,
            "high_value": high_value,
            "first_price": first_price_summary,
            "second_price": second_price_summary,
        },
    }
