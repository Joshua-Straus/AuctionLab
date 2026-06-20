import pytest

from auction_sim.agents import BanditAgent
from auction_sim.bandits import EpsilonGreedyPolicy
from auction_sim.learning import run_bandit_comparison
from market_sim.market_agents import BanditBuyerAgent


def test_policy_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        EpsilonGreedyPolicy(actions=[], epsilon=0.1)
    with pytest.raises(ValueError):
        EpsilonGreedyPolicy(actions=[0.5], epsilon=1.1)


def test_policy_updates_selected_action_reward():
    policy = EpsilonGreedyPolicy(actions=[0.5], epsilon=0.0, seed=1)

    assert policy.select_action() == 0.5
    policy.update(4.0)

    assert policy.action_counts[0.5] == 1
    assert policy.action_avg_rewards[0.5] == 4.0


def test_policy_is_deterministic_with_seed():
    first = EpsilonGreedyPolicy(actions=[0.5, 0.8, 1.0], epsilon=1.0, seed=7)
    second = EpsilonGreedyPolicy(actions=[0.5, 0.8, 1.0], epsilon=1.0, seed=7)

    assert [first.select_action() for _ in range(10)] == [
        second.select_action() for _ in range(10)
    ]


def test_bandit_agent_bids_valid_action_and_updates():
    agent = BanditAgent(agent_id="bandit", actions=[0.5], epsilon=0.0)

    assert agent.bid(100.0) == 50.0
    agent.update({"profit": 10.0})
    assert agent.action_avg_rewards[0.5] == 10.0


def test_bandit_buyer_uses_zero_reward_when_unmatched():
    agent = BanditBuyerAgent(
        agent_id="buyer",
        actions=[0.8],
        epsilon=0.0,
    )

    assert agent.bid(100.0) == 80.0
    agent.update({"traded": False, "profit": 0.0})
    assert agent.policy.action_avg_rewards[0.8] == 0.0


def test_bandit_comparison_returns_learning_analytics():
    result = run_bandit_comparison(num_rounds=20, seed=3)

    assert not result["cumulative_profit"].empty
    assert set(result["action_summary"].columns) == {
        "action",
        "count",
        "total_reward",
        "avg_reward",
    }
    assert len(result["action_history"]) == 20
