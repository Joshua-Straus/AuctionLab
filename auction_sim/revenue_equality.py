"""Paired Monte Carlo test of revenue equivalence across auction formats."""

from __future__ import annotations

import math
from collections.abc import Callable
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import f as f_distribution
from scipy.stats import ttest_rel

from auction_sim.agents import Agent, EquilibriumFirstPriceAgent, TruthfulAgent
from auction_sim.config import ExperimentConfig
from auction_sim.experiments import run_experiment


def _make_agents(
    agent_factory: Callable[[str], Agent],
    bidder_count: int,
) -> list[Agent]:
    return [agent_factory(f"bidder_{index}") for index in range(bidder_count)]


def _repeated_measures_anova(revenues: pd.DataFrame) -> dict[str, float | int | bool]:
    """Calculate a one-factor repeated-measures ANOVA from a complete matrix."""
    values = revenues.to_numpy(dtype=float)
    subject_count, format_count = values.shape
    grand_mean = values.mean()
    format_sum_squares = subject_count * np.square(
        values.mean(axis=0) - grand_mean
    ).sum()
    subject_sum_squares = format_count * np.square(
        values.mean(axis=1) - grand_mean
    ).sum()
    total_sum_squares = np.square(values - grand_mean).sum()
    error_sum_squares = max(
        0.0,
        total_sum_squares - format_sum_squares - subject_sum_squares,
    )
    format_df = format_count - 1
    error_df = (subject_count - 1) * format_df
    if error_sum_squares == 0:
        statistic = math.inf if format_sum_squares > 0 else 0.0
    else:
        statistic = (format_sum_squares / format_df) / (
            error_sum_squares / error_df
        )
    p_value = float(f_distribution.sf(statistic, format_df, error_df))
    return {
        "statistic": float(statistic),
        "format_degrees_of_freedom": format_df,
        "error_degrees_of_freedom": error_df,
        "p_value": p_value,
        "alpha": 0.05,
        "null_hypothesis_rejected": p_value < 0.05,
    }


def _holm_pairwise_comparisons(revenues: pd.DataFrame) -> list[dict[str, object]]:
    """Run paired t-tests and adjust their p-values with Holm's method."""
    comparisons: list[dict[str, object]] = []
    for first_format, second_format in combinations(revenues.columns, 2):
        first = revenues[first_format]
        second = revenues[second_format]
        differences = first - second
        if np.allclose(differences, 0.0):
            statistic, p_value = 0.0, 1.0
        elif np.isclose(differences.std(), 0.0):
            statistic = math.copysign(math.inf, float(differences.mean()))
            p_value = 0.0
        else:
            test = ttest_rel(first, second)
            statistic, p_value = float(test.statistic), float(test.pvalue)
        comparisons.append(
            {
                "first_format": first_format,
                "second_format": second_format,
                "mean_difference": float(differences.mean()),
                "statistic": statistic,
                "raw_p_value": p_value,
            }
        )

    ordered = sorted(
        enumerate(comparisons),
        key=lambda item: item[1]["raw_p_value"],
    )
    running_adjusted_p = 0.0
    comparison_count = len(comparisons)
    for rank, (original_index, details) in enumerate(ordered):
        adjusted_p = min(
            1.0,
            (comparison_count - rank) * float(details["raw_p_value"]),
        )
        running_adjusted_p = max(running_adjusted_p, adjusted_p)
        comparisons[original_index]["holm_adjusted_p_value"] = running_adjusted_p
        comparisons[original_index]["significant"] = running_adjusted_p < 0.05
    return comparisons


def _statistical_statement(
    anova: dict[str, float | int | bool],
    pairwise: list[dict[str, object]],
) -> str:
    p_value = float(anova["p_value"])
    p_text = "p < 0.001" if p_value < 0.001 else f"p = {p_value:.3f}"
    test_text = (
        "Average revenue differed across auction types"
        if anova["null_hypothesis_rejected"]
        else "The test found no evidence that average revenue differed across auction types"
    )
    statement = (
        f"{test_text} (repeated-measures ANOVA, "
        f"F({anova['format_degrees_of_freedom']}, "
        f"{anova['error_degrees_of_freedom']}) = "
        f"{float(anova['statistic']):.2f}, {p_text})."
    )
    if not anova["null_hypothesis_rejected"]:
        return statement

    significant_pairs = [item for item in pairwise if item["significant"]]
    if not significant_pairs:
        return statement + " No pair remained significant after Holm correction."
    pair_descriptions = []
    for details in significant_pairs:
        difference = float(details["mean_difference"])
        higher = (
            details["first_format"] if difference > 0 else details["second_format"]
        )
        lower = (
            details["second_format"] if difference > 0 else details["first_format"]
        )
        pair_descriptions.append(f"{higher} exceeded {lower}")
    return statement + " After Holm correction, " + "; ".join(pair_descriptions) + "."


def run_revenue_equality_experiment(
    num_rounds: int = 10_000,
    bidder_count: int = 16,
    low_value: float = 0.0,
    high_value: float = 100.0,
    seed: int = 42,
) -> dict:
    """Compare revenue across four theoretically equivalent auction formats."""
    if num_rounds <= 0:
        raise ValueError("num_rounds must be positive.")
    if bidder_count < 2:
        raise ValueError("bidder_count must be at least 2.")
    if low_value >= high_value:
        raise ValueError("Valuation range must have positive width.")

    config_values = {
        "num_rounds": num_rounds,
        "low_value": low_value,
        "high_value": high_value,
        "seed": seed,
    }
    formats: tuple[
        tuple[str, str, Callable[[str], Agent]], ...
    ] = (
        ("first_price", "First price", EquilibriumFirstPriceAgent),
        ("second_price", "Second price", TruthfulAgent),
        ("theoretical_english", "English", TruthfulAgent),
        ("theoretical_dutch", "Dutch", EquilibriumFirstPriceAgent),
    )

    revenue_frames: list[pd.DataFrame] = []
    auction_summaries: dict[str, dict[str, object]] = {}
    for auction_type, display_name, agent_factory in formats:
        results, _, summary = run_experiment(
            config=ExperimentConfig(
                auction_type=auction_type,
                **config_values,
            ),
            agents=_make_agents(agent_factory, bidder_count),
        )
        revenue_frames.append(
            results.drop_duplicates("round_id")
            [["round_id", "seller_revenue"]]
            .assign(auction_format=display_name)
        )
        auction_summaries[auction_type] = summary

    revenue_by_trial = pd.concat(revenue_frames, ignore_index=True)[
        ["round_id", "auction_format", "seller_revenue"]
    ]
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

    revenue_wide = revenue_by_trial.pivot(
        index="round_id",
        columns="auction_format",
        values="seller_revenue",
    )
    anova = _repeated_measures_anova(revenue_wide)
    pairwise = (
        _holm_pairwise_comparisons(revenue_wide)
        if anova["null_hypothesis_rejected"]
        else []
    )

    averages = format_summary.set_index("auction_format")[
        "average_seller_revenue"
    ]
    first_difference = revenue_wide["First price"] - revenue_wide["Second price"]
    theoretical_revenue = low_value + (
        (high_value - low_value) * (bidder_count - 1) / (bidder_count + 1)
    )
    comparison = {
        "question": (
            "Do equilibrium first-price and Dutch auctions and truthful "
            "second-price and English auctions produce equal expected revenue?"
        ),
        "first_price_average_revenue": float(averages["First price"]),
        "second_price_average_revenue": float(averages["Second price"]),
        "english_average_revenue": float(averages["English"]),
        "dutch_average_revenue": float(averages["Dutch"]),
        "average_revenue_difference": float(first_difference.mean()),
        "relative_difference_percent": (
            float(first_difference.mean())
            / float(averages["Second price"])
            * 100.0
            if averages["Second price"] != 0
            else 0.0
        ),
        "theoretical_expected_revenue": theoretical_revenue,
        "repeated_measures_anova": anova,
        "pairwise_comparisons": pairwise,
        "consistent_with_revenue_equality": not anova[
            "null_hypothesis_rejected"
        ],
        "interpretation": _statistical_statement(anova, pairwise),
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
            **auction_summaries,
        },
    }
