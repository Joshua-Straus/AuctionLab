"""Dedicated comparison of bidding strategies in first-price auctions."""

from __future__ import annotations

from auction_sim.agents import (
    BanditAgent,
    EquilibriumFirstPriceAgent,
    RandomAgent,
    ShadingAgent,
    TruthfulAgent,
)
from auction_sim.config import ExperimentConfig
from auction_sim.experiments import run_experiment


def run_first_price_strategy_experiment(
    num_rounds: int = 5_000,
    agents_per_strategy: int = 3,
    shading_alpha: float = 0.8,
    epsilon: float = 0.1,
    low_value: float = 0.0,
    high_value: float = 100.0,
    seed: int = 42,
) -> dict:
    """Compare all available bidder types in repeated first-price auctions."""
    if not 1 <= agents_per_strategy <= 3:
        raise ValueError("agents_per_strategy must be between 1 and 3.")

    agents = []
    strategy_by_agent: dict[str, str] = {}
    for index in range(agents_per_strategy):
        cohort = (
            (
                TruthfulAgent(agent_id=f"truthful_{index}"),
                "Truthful",
            ),
            (
                RandomAgent(agent_id=f"random_{index}"),
                "Random",
            ),
            (
                ShadingAgent(
                    agent_id=f"shading_{index}",
                    alpha=shading_alpha,
                ),
                f"Shading ({shading_alpha:.2f}×)",
            ),
            (
                BanditAgent(
                    agent_id=f"bandit_{index}",
                    epsilon=epsilon,
                    seed=seed + index,
                ),
                "Bandit",
            ),
            (
                EquilibriumFirstPriceAgent(agent_id=f"equilibrium_{index}"),
                "Equilibrium",
            ),
        )
        for agent, strategy in cohort:
            agents.append(agent)
            strategy_by_agent[agent.agent_id] = strategy

    results, agent_summary, auction_summary = run_experiment(
        config=ExperimentConfig(
            auction_type="first_price",
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
    leader = strategy_summary.iloc[0]
    equilibrium_caveat = (
        "The equilibrium bidders compete in a mixed-strategy environment with "
        "other bidder types, so the symmetric-equilibrium bid is not necessarily "
        "a best response in this comparison."
    )
    comparison = {
        "question": "Which agent type makes the most profit on average?",
        "highest_profit_strategy": str(leader["strategy"]),
        "highest_expected_profit": float(leader["expected_profit"]),
        "num_agent_types": int(strategy_summary["strategy"].nunique()),
        "total_agents": len(agents),
        "equilibrium_bid_multiplier": (len(agents) - 1) / len(agents),
        "equilibrium_value_lower_bound": low_value,
        "equilibrium_caveat": equilibrium_caveat,
        "interpretation": (
            f"{leader['strategy']} earned the highest mean profit per bidder-round "
            f"in this simulation. {equilibrium_caveat}"
        ),
    }
    return {
        "results": results,
        "agent_summary": agent_summary,
        "strategy_summary": strategy_summary,
        "auction_summary": auction_summary,
        "comparison": comparison,
    }
