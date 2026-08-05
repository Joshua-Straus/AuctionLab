from __future__ import annotations

from auction_sim.agents import (
    Agent,
    BanditAgent,
    ShadingAgent,
    TruthfulAgent,
)
from auction_sim.config import ExperimentConfig
from auction_sim.experiments import run_experiment
from auction_sim.learning import run_bandit_comparison


def _validate_participant_count(count: int, label: str) -> None:
    if not 1 <= count <= 16:
        raise ValueError(f"{label} must be between 1 and 16.")


def _make_dashboard_agents(
    strategy: str,
    bidder_count: int,
    alpha: float,
    seed: int,
) -> list[Agent]:
    def make_agent(index: int, selected_strategy: str) -> Agent:
        if selected_strategy == "truthful":
            return TruthfulAgent(agent_id=f"truthful_{index}")
        if selected_strategy == "shading":
            return ShadingAgent(agent_id=f"shade_{index}", alpha=alpha)
        if selected_strategy == "bandit":
            return BanditAgent(agent_id=f"bandit_{index}", seed=seed + index)
        raise ValueError(f"Unknown auction strategy: {selected_strategy}")

    if strategy == "mixed":
        strategies = ("truthful", "shading", "bandit")
        return [
            make_agent(index, strategies[index % len(strategies)])
            for index in range(bidder_count)
        ]

    return [make_agent(index, strategy) for index in range(bidder_count)]


def run_auction_dashboard(
    auction_type: str,
    num_rounds: int,
    bidder_count: int,
    strategy: str,
    alpha: float,
    low_value: float,
    high_value: float,
    seed: int,
) -> dict:
    _validate_participant_count(bidder_count, "Bidder count")
    if num_rounds <= 0:
        raise ValueError("Number of rounds must be positive.")
    if low_value > high_value:
        raise ValueError("Valuation range is invalid.")

    agents = _make_dashboard_agents(strategy, bidder_count, alpha, seed)

    config = ExperimentConfig(
        auction_type=auction_type,
        num_rounds=num_rounds,
        low_value=low_value,
        high_value=high_value,
        seed=seed,
    )
    results, agents_summary, auction_summary = run_experiment(
        config=config,
        agents=agents,
    )
    return {
        "results": results,
        "agent_summary": agents_summary,
        "auction_summary": auction_summary,
    }


def run_learning_dashboard(
    num_rounds: int,
    epsilon: float,
    seed: int,
) -> dict:
    return run_bandit_comparison(
        num_rounds=num_rounds,
        epsilon=epsilon,
        seed=seed,
    )
