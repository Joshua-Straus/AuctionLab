from __future__ import annotations

from dataclasses import dataclass, field

from auction_sim.agents import validate_alpha, validate_value
from auction_sim.bandits import EpsilonGreedyPolicy


@dataclass
class BuyerAgent:
    agent_id: str

    def bid(self, value: float, context: dict | None = None) -> float:
        raise NotImplementedError("Subclasses must implement bid().")

    def update(self, result: dict) -> None:
        pass


@dataclass
class SellerAgent:
    agent_id: str

    def ask(self, value: float, context: dict | None = None) -> float:
        raise NotImplementedError("Subclasses must implement ask().")

    def update(self, result: dict) -> None:
        pass


@dataclass
class TruthfulSellerAgent(SellerAgent):
    def ask(self, value: float, context: dict | None = None) -> float:
        validate_value(value)
        return value


@dataclass
class MarkupSellerAgent(SellerAgent):
    markup: float

    def __post_init__(self) -> None:
        validate_alpha(self.markup)

    def ask(self, value: float, context: dict | None = None) -> float:
        validate_value(value)
        return value * (1 + self.markup)


@dataclass
class TruthfulBuyerAgent(BuyerAgent):
    def bid(self, value: float, context: dict | None = None) -> float:
        validate_value(value)
        return value


@dataclass
class ShadingBuyerAgent(BuyerAgent):
    alpha: float

    def __post_init__(self) -> None:
        validate_alpha(self.alpha)

    def bid(self, value: float, context: dict | None = None) -> float:
        validate_value(value)
        return value * self.alpha


@dataclass
class BanditBuyerAgent(BuyerAgent):
    actions: list[float] = field(
        default_factory=lambda: [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
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
