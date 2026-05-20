from __future__ import annotations

from pathlib import Path

import pandas as pd

from auction_sim.agents import RandomAgent, ShadingAgent, TruthfulAgent
from auction_sim.auctions import Auction, FirstPriceAuction, SecondPriceAuction
from auction_sim.data import results_to_dataframe
from auction_sim.metrics import summarize_agents, summarize_auction
from auction_sim.simulation import Simulation
from auction_sim.plots import plot_agent_profit, plot_agent_win_rate

def make_baseline_agents():
    """
    Creates a standard set of agents for baseline auction experiments.
    """
    return [
        TruthfulAgent(agent_id="truthful"),
        ShadingAgent(agent_id="shade_60", alpha=0.60),
        ShadingAgent(agent_id="shade_70", alpha=0.70),
        ShadingAgent(agent_id="shade_80", alpha=0.80),
        ShadingAgent(agent_id="shade_90", alpha=0.90),
        RandomAgent(agent_id="random"),
    ]

def run_experiment(
    auction: Auction,
    num_rounds: int = 10_000,
    low_value: float = 0,
    high_value: float = 100,
    seed: int | None = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Runs one auction experiment and returns:
    - full round-level dataframe
    - agent summary dataframe
    - auction summary dictionary
    """

    agents = make_baseline_agents()

    sim = Simulation(
        auction=auction,
        agents=agents,
        num_rounds=num_rounds,
        low_value=low_value,
        high_value=high_value,
        seed=seed,
    )

    results = sim.run()
    df = results_to_dataframe(results)

    agent_summary = summarize_agents(df)
    auction_summary = summarize_auction(df)

    return df, agent_summary, auction_summary


def run_baseline_comparison(
    num_rounds: int = 10_000,
    output_dir: str = "outputs",
) -> dict[str, dict]:
    """
    Runs baseline experiments for first-price and second-price auctions.
    Saves outputs to CSV.
    """

    Path(output_dir).mkdir(exist_ok=True)

    experiments = {
        "first_price": FirstPriceAuction(),
        "second_price": SecondPriceAuction(),
    }

    all_results = {}

    for name, auction in experiments.items():
        df, agent_summary, auction_summary = run_experiment(
            auction=auction,
            num_rounds=num_rounds,
            seed=42,
        )

        df.to_csv(f"{output_dir}/{name}_results.csv", index=False)
        agent_summary.to_csv(f"{output_dir}/{name}_agent_summary.csv", index=False)

        plot_agent_profit(
            agent_summary,
            output_path=f"{output_dir}/{name}_agent_profit.png",
        )

        plot_agent_win_rate(
            agent_summary,
            output_path=f"{output_dir}/{name}_agent_win_rate.png",
        )

        all_results[name] = {
            "results": df,
            "agent_summary": agent_summary,
            "auction_summary": auction_summary,
        }

    return all_results