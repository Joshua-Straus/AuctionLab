from market_sim.experiments import (
    make_market_agents,
    run_market_scenario,
    run_market_scenarios,
)


def test_make_market_agents_supports_truthful_and_strategic_agents():
    buyers, sellers = make_market_agents(
        num_buyers=3,
        num_sellers=2,
        buyer_strategy="shading",
        seller_strategy="markup",
    )

    assert len(buyers) == 3
    assert len(sellers) == 2


def test_market_scenario_returns_and_saves_analytics(tmp_path):
    result = run_market_scenario(
        scenario_name="test",
        num_buyers=2,
        num_sellers=2,
        num_rounds=10,
        output_dir=str(tmp_path),
    )

    assert not result["results"].empty
    assert not result["agent_summary"].empty
    assert result["market_summary"]["num_rounds"] == 10
    assert (tmp_path / "test_market_results.csv").exists()
    assert (tmp_path / "test_market_agents.csv").exists()
    assert (tmp_path / "test_market_summary.csv").exists()


def test_market_scenarios_include_competition_imbalances(tmp_path):
    summary = run_market_scenarios(
        num_rounds=5,
        output_dir=str(tmp_path),
    )

    assert {"buyer_heavy", "balanced", "seller_heavy"}.issubset(
        set(summary["scenario"])
    )
    assert (tmp_path / "market_scenarios_summary.csv").exists()
