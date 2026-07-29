"""Dedicated experiment for truthful bidding in second-price auctions."""

from __future__ import annotations

import pandas as pd

from auction_sim.agents import BanditAgent, ShadingAgent, TruthfulAgent
from auction_sim.config import ExperimentConfig
from auction_sim.experiments import run_experiment


def run_vickrey_dominance_experiment(
    num_rounds: int = 5_000,
    agents_per_strategy: int = 3,
    shading_alpha: float = 0.8,
    epsilon: float = 0.1,
    low_value: float = 0.0,
    high_value: float = 100.0,
    seed: int = 42,
) -> dict:
    """Compare truthful, shaded, and adaptive bids in a Vickrey auction."""
    if not 1 <= agents_per_strategy <= 5:
        raise ValueError("agents_per_strategy must be between 1 and 5.")

    agents = []
    strategy_by_agent: dict[str, str] = {}
    for index in range(agents_per_strategy):
        truthful_id = f"truthful_{index}"
        shading_id = f"shading_{index}"
        bandit_id = f"bandit_{index}"
        agents.extend(
            [
                TruthfulAgent(agent_id=truthful_id),
                ShadingAgent(agent_id=shading_id, alpha=shading_alpha),
                BanditAgent(
                    agent_id=bandit_id,
                    epsilon=epsilon,
                    seed=seed + index,
                ),
            ]
        )
        strategy_by_agent.update(
            {
                truthful_id: "Truthful",
                shading_id: f"Shading ({shading_alpha:.2f}×)",
                bandit_id: "Bandit",
            }
        )

    results, agent_summary, auction_summary = run_experiment(
        config=ExperimentConfig(
            auction_type="second_price",
            num_rounds=num_rounds,
            low_value=low_value,
            high_value=high_value,
            seed=seed,
        ),
        agents=agents,
    )
    results = results.assign(strategy=results["agent_id"].map(strategy_by_agent))
    results["bid_to_value"] = (
        results["bid"] / results["valuation"].where(results["valuation"] != 0)
    ).fillna(0.0)
    agent_summary = agent_summary.assign(
        strategy=agent_summary["agent_id"].map(strategy_by_agent)
    )
    strategy_summary = (
        results.groupby("strategy", as_index=False)
        .agg(
            expected_profit=("profit", "mean"),
            total_profit=("profit", "sum"),
            win_rate=("is_winner", "mean"),
            avg_bid=("bid", "mean"),
            avg_valuation=("valuation", "mean"),
            avg_bid_to_value=("bid_to_value", "mean"),
        )
        .sort_values("expected_profit", ascending=False)
    )

    profit_by_strategy = strategy_summary.set_index("strategy")["expected_profit"]
    truthful_profit = float(profit_by_strategy["Truthful"])
    shading_label = f"Shading ({shading_alpha:.2f}×)"
    shading_profit = float(profit_by_strategy[shading_label])
    bandit_profit = float(profit_by_strategy["Bandit"])
    tolerance = max(0.01, abs(truthful_profit) * 0.01)
    supports_proposition = (
        truthful_profit + tolerance >= shading_profit
        and truthful_profit + tolerance >= bandit_profit
    )
    proposition = {
        "statement": (
            "Bidding your valuation is a weakly-dominant strategy in a "
            "second-price auction."
        ),
        "truthful_expected_profit": truthful_profit,
        "shading_expected_profit": shading_profit,
        "bandit_expected_profit": bandit_profit,
        "truthful_advantage_over_shading": truthful_profit - shading_profit,
        "truthful_advantage_over_bandit": truthful_profit - bandit_profit,
        "supports_proposition": supports_proposition,
        "interpretation": (
            "The simulated expected-profit ordering is consistent with the proposition."
            if supports_proposition
            else "Sampling variation is not consistent with the expected ordering; run more rounds."
        ),
    }
    return {
        "results": results,
        "agent_summary": agent_summary,
        "strategy_summary": strategy_summary,
        "auction_summary": auction_summary,
        "proposition": proposition,
    }
