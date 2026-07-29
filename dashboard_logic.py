from __future__ import annotations

from auction_sim.agents import (
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

    if strategy == "truthful":
        agents = [
            TruthfulAgent(agent_id=f"truthful_{index}")
            for index in range(bidder_count)
        ]
    elif strategy == "shading":
        agents = [
            ShadingAgent(agent_id=f"shade_{index}", alpha=alpha)
            for index in range(bidder_count)
        ]
    elif strategy == "bandit":
        agents = [
            BanditAgent(
                agent_id=f"bandit_{index}",
                seed=seed + index,
            )
            for index in range(bidder_count)
        ]
    elif strategy == "mixed":
        agents = []
        for index in range(bidder_count):
            mode = index % 3
            if mode == 0:
                agents.append(TruthfulAgent(agent_id=f"truthful_{index}"))
            elif mode == 1:
                agents.append(
                    ShadingAgent(
                        agent_id=f"shade_{index}",
                        alpha=alpha,
                    )
                )
            else:
                agents.append(
                    BanditAgent(
                        agent_id=f"bandit_{index}",
                        seed=seed + index,
                    )
                )
    else:
        raise ValueError(f"Unknown auction strategy: {strategy}")

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
