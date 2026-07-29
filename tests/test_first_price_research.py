import pytest

from auction_sim.agents import EquilibriumFirstPriceAgent
from auction_sim.first_price_research import run_first_price_strategy_experiment


def test_equilibrium_first_price_agent_uses_number_of_agents():
    agent = EquilibriumFirstPriceAgent(agent_id="equilibrium")

    assert agent.bid(100.0, {"num_agents": 5}) == pytest.approx(80.0)


def test_equilibrium_first_price_agent_requires_participant_context():
    agent = EquilibriumFirstPriceAgent(agent_id="equilibrium")

    with pytest.raises(ValueError):
        agent.bid(100.0)


def test_first_price_experiment_compares_every_agent_type():
    result = run_first_price_strategy_experiment(
        num_rounds=300,
        agents_per_strategy=2,
        seed=42,
    )

    assert set(result["results"]["auction_type"]) == {"first_price"}
    assert set(result["strategy_summary"]["strategy"]) == {
        "Truthful",
        "Random",
        "Shading (0.80×)",
        "Bandit",
        "Equilibrium",
    }
    assert result["comparison"]["num_agent_types"] == 5
    assert result["comparison"]["highest_profit_strategy"] in set(
        result["strategy_summary"]["strategy"]
    )
