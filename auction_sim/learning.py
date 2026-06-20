from __future__ import annotations

import pandas as pd

from auction_sim.agents import BanditAgent, ShadingAgent
from auction_sim.config import ExperimentConfig
from auction_sim.experiments import run_experiment


def cumulative_profit_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    ordered = df.sort_values(["agent_id", "round_id"]).copy()
    ordered["cumulative_profit"] = ordered.groupby("agent_id")[
        "profit"
    ].cumsum()
    return ordered[
        ["round_id", "agent_id", "profit", "cumulative_profit"]
    ]


def run_bandit_comparison(
    num_rounds: int = 1_000,
    epsilon: float = 0.1,
    seed: int | None = 42,
) -> dict:
    bandit = BanditAgent(
        agent_id="bandit",
        epsilon=epsilon,
        seed=seed,
    )
    agents = [
        bandit,
        ShadingAgent(agent_id="fixed_70", alpha=0.7),
        ShadingAgent(agent_id="fixed_80", alpha=0.8),
        ShadingAgent(agent_id="fixed_90", alpha=0.9),
    ]
    config = ExperimentConfig(
        auction_type="first_price",
        num_rounds=num_rounds,
        seed=seed,
    )
    df, agent_summary, auction_summary = run_experiment(
        config=config,
        agents=agents,
    )
    return {
        "results": df,
        "agent_summary": agent_summary,
        "auction_summary": auction_summary,
        "cumulative_profit": cumulative_profit_dataframe(df),
        "action_summary": bandit.policy.summary_dataframe(),
        "action_history": pd.DataFrame(
            {
                "round_id": range(1, len(bandit.policy.action_history) + 1),
                "action": bandit.policy.action_history,
                "reward": bandit.policy.reward_history,
            }
        ),
    }
