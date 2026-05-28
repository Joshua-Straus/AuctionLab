"""
File to store different agent strategies for auctions.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


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
