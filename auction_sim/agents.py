from __future__ import annotations
import random
from dataclasses import dataclass


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
        return value

@dataclass
class RandomAgent(Agent):
    """
    Agent that bids a random amount between 0 and its valuation.
    """

    def bid(self, value: float, context: dict | None = None) -> float:
        return random.uniform(0, value)

@dataclass
class ShadingAgent(Agent):
    """
    Agent that bids a fraction of its valuation.
    """

    alpha: float  # Default to bidding 75% of valuation

    def bid(self, value: float, context: dict | None = None) -> float:
        return value * self.alpha