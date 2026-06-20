from __future__ import annotations

import random
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class EpsilonGreedyPolicy:
    actions: list[float]
    epsilon: float = 0.1
    seed: int | None = 42
    action_counts: dict[float, int] = field(init=False)
    action_total_rewards: dict[float, float] = field(init=False)
    action_avg_rewards: dict[float, float] = field(init=False)
    last_action: float | None = field(default=None, init=False)
    action_history: list[float] = field(default_factory=list, init=False)
    reward_history: list[float] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if not self.actions:
            raise ValueError("Bandit actions cannot be empty.")
        if len(set(self.actions)) != len(self.actions):
            raise ValueError("Bandit actions must be unique.")
        if not 0 <= self.epsilon <= 1:
            raise ValueError("epsilon must be between 0 and 1.")

        self.actions = list(self.actions)
        self.action_counts = {action: 0 for action in self.actions}
        self.action_total_rewards = {
            action: 0.0 for action in self.actions
        }
        self.action_avg_rewards = {action: 0.0 for action in self.actions}
        self._rng = random.Random(self.seed)

    def select_action(self) -> float:
        if self._rng.random() < self.epsilon:
            action = self._rng.choice(self.actions)
        else:
            best_reward = max(self.action_avg_rewards.values())
            best_actions = [
                action
                for action in self.actions
                if self.action_avg_rewards[action] == best_reward
            ]
            action = self._rng.choice(best_actions)

        self.last_action = action
        self.action_history.append(action)
        return action

    def update(self, reward: float) -> None:
        if self.last_action is None:
            raise ValueError("Select an action before updating the policy.")

        action = self.last_action
        self.action_counts[action] += 1
        self.action_total_rewards[action] += reward
        self.action_avg_rewards[action] = (
            self.action_total_rewards[action] / self.action_counts[action]
        )
        self.reward_history.append(reward)

    def summary_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "action": action,
                    "count": self.action_counts[action],
                    "total_reward": self.action_total_rewards[action],
                    "avg_reward": self.action_avg_rewards[action],
                }
                for action in self.actions
            ]
        )
