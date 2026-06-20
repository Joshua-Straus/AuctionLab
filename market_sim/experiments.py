from __future__ import annotations

from pathlib import Path

import pandas as pd

from market_sim.data import market_results_to_dataframe
from market_sim.market_agents import (
    BanditBuyerAgent,
    MarkupSellerAgent,
    ShadingBuyerAgent,
    TruthfulBuyerAgent,
    TruthfulSellerAgent,
)
from market_sim.metrics import summarize_market, summarize_market_agents
from market_sim.simulation import MarketSimulation


def run_market_experiment(
    buyers,
    sellers,
    num_rounds: int = 1_000,
    buyer_value_low: float = 0.0,
    buyer_value_high: float = 100.0,
    seller_cost_low: float = 0.0,
    seller_cost_high: float = 100.0,
    seed: int | None = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    simulation = MarketSimulation(
        buyers=buyers,
        sellers=sellers,
        num_rounds=num_rounds,
        buyer_value_low=buyer_value_low,
        buyer_value_high=buyer_value_high,
        seller_cost_low=seller_cost_low,
        seller_cost_high=seller_cost_high,
        seed=seed,
    )
    df = market_results_to_dataframe(simulation.run())
    return df, summarize_market_agents(df), summarize_market(df)


def make_market_agents(
    num_buyers: int,
    num_sellers: int,
    buyer_strategy: str = "truthful",
    seller_strategy: str = "truthful",
    buyer_alpha: float = 0.8,
    seller_markup: float = 0.2,
    seed: int | None = 42,
):
    if buyer_strategy == "truthful":
        buyers = [
            TruthfulBuyerAgent(agent_id=f"buyer_{index}")
            for index in range(num_buyers)
        ]
    elif buyer_strategy == "shading":
        buyers = [
            ShadingBuyerAgent(
                agent_id=f"buyer_{index}",
                alpha=buyer_alpha,
            )
            for index in range(num_buyers)
        ]
    elif buyer_strategy == "bandit":
        buyers = [
            BanditBuyerAgent(
                agent_id=f"buyer_{index}",
                seed=None if seed is None else seed + index,
            )
            for index in range(num_buyers)
        ]
    else:
        raise ValueError(f"Unknown buyer strategy: {buyer_strategy}")

    if seller_strategy == "truthful":
        sellers = [
            TruthfulSellerAgent(agent_id=f"seller_{index}")
            for index in range(num_sellers)
        ]
    elif seller_strategy == "markup":
        sellers = [
            MarkupSellerAgent(
                agent_id=f"seller_{index}",
                markup=seller_markup,
            )
            for index in range(num_sellers)
        ]
    else:
        raise ValueError(f"Unknown seller strategy: {seller_strategy}")

    return buyers, sellers


def run_market_scenario(
    scenario_name: str,
    num_buyers: int,
    num_sellers: int,
    buyer_strategy: str = "truthful",
    seller_strategy: str = "truthful",
    buyer_alpha: float = 0.8,
    seller_markup: float = 0.2,
    num_rounds: int = 1_000,
    seed: int | None = 42,
    output_dir: str = "outputs",
) -> dict:
    buyers, sellers = make_market_agents(
        num_buyers=num_buyers,
        num_sellers=num_sellers,
        buyer_strategy=buyer_strategy,
        seller_strategy=seller_strategy,
        buyer_alpha=buyer_alpha,
        seller_markup=seller_markup,
        seed=seed,
    )
    df, agent_summary, market_summary = run_market_experiment(
        buyers=buyers,
        sellers=sellers,
        num_rounds=num_rounds,
        seed=seed,
    )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path / f"{scenario_name}_market_results.csv", index=False)
    agent_summary.to_csv(
        output_path / f"{scenario_name}_market_agents.csv",
        index=False,
    )
    pd.DataFrame([{**market_summary, "scenario": scenario_name}]).to_csv(
        output_path / f"{scenario_name}_market_summary.csv",
        index=False,
    )
    return {
        "results": df,
        "agent_summary": agent_summary,
        "market_summary": market_summary,
    }


def run_market_scenarios(
    num_rounds: int = 1_000,
    seed: int | None = 42,
    output_dir: str = "outputs",
) -> pd.DataFrame:
    scenarios = [
        ("truthful", 8, 8, "truthful", "truthful"),
        ("strategic", 8, 8, "shading", "markup"),
        ("buyer_heavy", 12, 6, "truthful", "truthful"),
        ("balanced", 8, 8, "truthful", "truthful"),
        ("seller_heavy", 6, 12, "truthful", "truthful"),
    ]
    rows = []
    for name, buyers, sellers, buyer_strategy, seller_strategy in scenarios:
        result = run_market_scenario(
            scenario_name=name,
            num_buyers=buyers,
            num_sellers=sellers,
            buyer_strategy=buyer_strategy,
            seller_strategy=seller_strategy,
            num_rounds=num_rounds,
            seed=seed,
            output_dir=output_dir,
        )
        rows.append(
            {
                "scenario": name,
                "num_buyers": buyers,
                "num_sellers": sellers,
                **result["market_summary"],
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(
        Path(output_dir) / "market_scenarios_summary.csv",
        index=False,
    )
    return summary
