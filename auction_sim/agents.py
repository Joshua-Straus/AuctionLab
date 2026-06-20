"""
File to store different agent strategies for auctions.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from auction_sim.bandits import EpsilonGreedyPolicy


def validate_value(value: float) -> None:
    if value < 0:
        raise ValueError("Private valuation cannot be negative.")


def validate_alpha(alpha: float) -> None:
    if alpha < 0:
        raise ValueError("Alpha must be nonnegative.")


@dataclass
class Agent:
    """
    Base class for all auction agents.

    Each agent receives a private valuation and returns a bid.
    """

    agent_id: str

    def bid(self, value: float, context: dict | None = None) -> float:
        raise NotImplementedError("Subclasses must implement bid().")

    def update(self, result: dict) -> None:
        """
        Optional learning/update method.
        Simple agents will ignore this.
        Adaptive agents will use this later.
        """
        pass

@dataclass
class TruthfulAgent(Agent):
    """
    Agent that always bids its true valuation.
    """

    def bid(self, value: float, context: dict | None = None) -> float:
        validate_value(value)
        return value

@dataclass
class RandomAgent(Agent):
    """
    Agent that bids a random amount between 0 and its valuation.
    """

    def bid(self, value: float, context: dict | None = None) -> float:
        validate_value(value)
        return random.uniform(0, value)

@dataclass
class ShadingAgent(Agent):
    """
    Agent that bids a fraction of its valuation.
    """

    alpha: float

    def __post_init__(self) -> None:
        validate_alpha(self.alpha)

    def bid(self, value: float, context: dict | None = None) -> float:
        validate_value(value)
        return value * self.alpha


@dataclass
class BanditAgent(Agent):
    actions: list[float] = field(
        default_factory=lambda: [0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0]
    )
    epsilon: float = 0.1
    seed: int | None = 42
    policy: EpsilonGreedyPolicy = field(init=False)

    def __post_init__(self) -> None:
        for action in self.actions:
            validate_alpha(action)
        self.policy = EpsilonGreedyPolicy(
            actions=self.actions,
            epsilon=self.epsilon,
            seed=self.seed,
        )

    def bid(self, value: float, context: dict | None = None) -> float:
        validate_value(value)
        return self.policy.select_action() * value

    def update(self, result: dict) -> None:
        self.policy.update(float(result.get("profit", 0.0)))

    @property
    def action_counts(self) -> dict[float, int]:
        return self.policy.action_counts

    @property
    def action_avg_rewards(self) -> dict[float, float]:
        return self.policy.action_avg_rewards

    @property
    def last_action(self) -> float | None:
        return self.policy.last_action
