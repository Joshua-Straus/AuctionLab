"""
File to define functions for running auction experiments, including baseline comparisons.
"""


from __future__ import annotations

from pathlib import Path

import pandas as pd

from auction_sim.agents import RandomAgent, ShadingAgent, TruthfulAgent
from auction_sim.auctions import Auction, FirstPriceAuction, SecondPriceAuction
from auction_sim.config import ExperimentConfig
from auction_sim.data import results_to_dataframe
from auction_sim.metrics import summarize_agents, summarize_auction
from auction_sim.plots import plot_agent_profit, plot_agent_win_rate
from auction_sim.simulation import Simulation


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


def make_auction(auction_type: str) -> Auction:
    """
    Creates an auction object from a string name.
    """
    if auction_type == "first_price":
        return FirstPriceAuction()

    if auction_type == "second_price":
        return SecondPriceAuction()

    raise ValueError(f"Unknown auction type: {auction_type}")


def run_experiment(
    config: ExperimentConfig | None = None,
    *,
    auction: Auction | None = None,
    auction_type: str | None = None,
    num_rounds: int | None = None,
    low_value: float | None = None,
    high_value: float | None = None,
    seed: int | None = None,
    agents=None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Runs one auction experiment and returns:
    - full round-level dataframe
    - agent summary dataframe
    - auction summary dictionary
    """
    if config is not None and any(
        x is not None
        for x in [
            auction,
            auction_type,
            num_rounds,
            low_value,
            high_value,
            seed,
        ]
    ):
        raise ValueError(
            "Pass either config=ExperimentConfig(...) or override arguments, not both."
        )

    if config is None:
        config = ExperimentConfig(
            auction_type=auction_type
            or (auction.auction_type if auction else "first_price"),
            num_rounds=num_rounds if num_rounds is not None else 10_000,
            low_value=low_value if low_value is not None else 0.0,
            high_value=high_value if high_value is not None else 100.0,
            seed=seed if seed is not None else 42,
        )

    selected_auction = auction if auction is not None else make_auction(config.auction_type)

    if agents is None:
        agents = make_baseline_agents()

    sim = Simulation(
        auction=selected_auction,
        agents=agents,
        num_rounds=config.num_rounds,
        low_value=config.low_value,
        high_value=config.high_value,
        seed=config.seed,
    )

    results = sim.run()
    df = results_to_dataframe(results)

    agent_summary = summarize_agents(df)
    auction_summary = summarize_auction(df)

    return df, agent_summary, auction_summary


def run_baseline_comparison(
    num_rounds: int | None = None,
    output_dir: str = "outputs",
) -> dict[str, dict]:
    """
    Runs baseline experiments for first-price and second-price auctions.
    Saves outputs to CSV.
    """

    Path(output_dir).mkdir(exist_ok=True)

    round_count = num_rounds if num_rounds is not None else 10_000

    all_results = {}

    for auction_type in ["first_price", "second_price"]:
        config = ExperimentConfig(
            auction_type=auction_type,
            num_rounds=round_count,
            low_value=0.0,
            high_value=100.0,
            seed=42,
            output_dir=output_dir,
        )

        df, agent_summary, auction_summary = run_experiment(config)

        df.to_csv(f"{output_dir}/{auction_type}_results.csv", index=False)
        agent_summary.to_csv(
            f"{output_dir}/{auction_type}_agent_summary.csv",
            index=False,
        )

        plot_agent_profit(
            agent_summary,
            output_path=f"{output_dir}/{auction_type}_agent_profit.png",
        )

        plot_agent_win_rate(
            agent_summary,
            output_path=f"{output_dir}/{auction_type}_agent_win_rate.png",
        )

        all_results[auction_type] = {
            "config": config,
            "results": df,
            "agent_summary": agent_summary,
            "auction_summary": auction_summary,
        }

    return all_results

def make_shading_competition_agents(
    num_agents: int,
    alpha: float = 0.8,
) -> list[ShadingAgent]:
    """
    Creates identical shading agents for competition experiments.
    """
    return [
        ShadingAgent(agent_id=f"shade_{alpha}_{i}", alpha=alpha)
        for i in range(num_agents)
    ]

def run_competition_sweep(
    bidder_counts: list[int] | None = None,
    num_rounds: int = 10_000,
    auction_type: str = "first_price",
    alpha: float = 0.8,
    low_value: float = 0.0,
    high_value: float = 100.0,
    seed: int | None = 42,
    output_dir: str = "outputs",
) -> pd.DataFrame:
    """
    Runs experiments with different numbers of bidders.

    Returns one row per bidder count.
    """
    if bidder_counts is None:
        bidder_counts = [2, 4, 8, 16, 32]

    Path(output_dir).mkdir(exist_ok=True)

    rows = []

    for num_agents in bidder_counts:
        agents = make_shading_competition_agents(
            num_agents=num_agents,
            alpha=alpha,
        )

        config = ExperimentConfig(
            auction_type=auction_type,
            num_rounds=num_rounds,
            low_value=low_value,
            high_value=high_value,
            seed=seed,
            output_dir=output_dir,
        )

        df, agent_summary, auction_summary = run_experiment(
            config=config,
            agents=agents,
        )

        rows.append(
            {
                "num_agents": num_agents,
                "alpha": alpha,
                "auction_type": auction_type,
                "num_rounds": num_rounds,
                "low_value": low_value,
                "high_value": high_value,
                **auction_summary,
                "avg_agent_profit": agent_summary["avg_profit"].mean(),
                "total_agent_profit": agent_summary["total_profit"].sum(),
            }
        )

    sweep_df = pd.DataFrame(rows)
    sweep_df.to_csv(Path(output_dir) / "competition_sweep.csv", index=False)

    return sweep_df
