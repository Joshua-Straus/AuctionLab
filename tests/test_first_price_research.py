import pytest

from auction_sim.agents import EquilibriumFirstPriceAgent
from auction_sim.first_price_research import run_first_price_strategy_experiment


def test_equilibrium_first_price_agent_uses_number_of_agents():
    agent = EquilibriumFirstPriceAgent(agent_id="equilibrium")

    assert agent.bid(100.0, {"num_agents": 5}) == pytest.approx(80.0)


def test_equilibrium_first_price_agent_uses_nonzero_lower_bound():
    agent = EquilibriumFirstPriceAgent(agent_id="equilibrium")

    assert agent.bid(
        100.0,
        {"num_agents": 5, "low_value": 25.0},
    ) == pytest.approx(85.0)


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
    assert "mixed-strategy environment" in result["comparison"][
        "equilibrium_caveat"
    ]


def test_first_price_experiment_passes_lower_bound_to_equilibrium_agents():
    result = run_first_price_strategy_experiment(
        num_rounds=20,
        agents_per_strategy=1,
        low_value=50.0,
        high_value=50.0,
        seed=42,
    )

    equilibrium_results = result["results"].query("strategy == 'Equilibrium'")
    assert set(equilibrium_results["bid"]) == {50.0}
