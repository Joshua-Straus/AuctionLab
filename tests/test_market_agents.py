import pytest

from market_sim.market_agents import (
    MarkupSellerAgent,
    ShadingBuyerAgent,
    TruthfulBuyerAgent,
    TruthfulSellerAgent,
)


def test_truthful_buyer_bids_private_value():
    agent = TruthfulBuyerAgent(agent_id="buyer")

    assert agent.bid(100.0) == 100.0


def test_shading_buyer_bids_alpha_fraction_of_value():
    agent = ShadingBuyerAgent(agent_id="buyer", alpha=0.8)

    assert agent.bid(100.0) == 80.0


def test_truthful_seller_asks_private_value():
    agent = TruthfulSellerAgent(agent_id="seller")

    assert agent.ask(40.0) == 40.0


def test_markup_seller_adds_markup_to_value():
    agent = MarkupSellerAgent(agent_id="seller", markup=0.25)

    assert agent.ask(40.0) == 50.0


@pytest.mark.parametrize(
    ("agent", "method_name"),
    [
        (TruthfulBuyerAgent(agent_id="buyer"), "bid"),
        (ShadingBuyerAgent(agent_id="shade", alpha=0.8), "bid"),
        (TruthfulSellerAgent(agent_id="seller"), "ask"),
        (MarkupSellerAgent(agent_id="markup", markup=0.2), "ask"),
    ],
)
def test_market_agents_reject_negative_private_values(agent, method_name):
    with pytest.raises(ValueError):
        getattr(agent, method_name)(-1.0)


def test_shading_buyer_rejects_negative_alpha():
    with pytest.raises(ValueError):
        ShadingBuyerAgent(agent_id="buyer", alpha=-0.1)


def test_markup_seller_rejects_negative_markup():
    with pytest.raises(ValueError):
        MarkupSellerAgent(agent_id="seller", markup=-0.1)
