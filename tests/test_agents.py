import pytest

from auction_sim.agents import RandomAgent, ShadingAgent, TruthfulAgent


def test_truthful_agent_bids_value():
    agent = TruthfulAgent(agent_id="truthful")
    assert agent.bid(100) == 100


def test_shading_agent_bids_fraction_of_value():
    agent = ShadingAgent(agent_id="shade_70", alpha=0.7)
    assert agent.bid(100) == 70


def test_random_agent_bid_is_between_zero_and_value():
    agent = RandomAgent(agent_id="random")

    for _ in range(100):
        bid = agent.bid(100)
        assert 0 <= bid <= 100


def test_truthful_agent_rejects_negative_value():
    agent = TruthfulAgent(agent_id="truthful")

    with pytest.raises(ValueError):
        agent.bid(-10)


def test_random_agent_rejects_negative_value():
    agent = RandomAgent(agent_id="random")

    with pytest.raises(ValueError):
        agent.bid(-10)


def test_shading_agent_rejects_negative_alpha():
    with pytest.raises(ValueError):
        ShadingAgent(agent_id="bad", alpha=-0.5)


def test_shading_agent_rejects_negative_value():
    agent = ShadingAgent(agent_id="shade", alpha=0.7)

    with pytest.raises(ValueError):
        agent.bid(-10)


def test_shading_agent_allows_alpha_greater_than_one():
    agent = ShadingAgent(agent_id="aggressive", alpha=1.1)

    assert agent.bid(100) == pytest.approx(110)
