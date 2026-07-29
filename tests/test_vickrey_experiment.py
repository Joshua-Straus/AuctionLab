import pytest

from auction_sim.vickrey import run_vickrey_dominance_experiment


def test_vickrey_experiment_compares_expected_profit_by_strategy():
    result = run_vickrey_dominance_experiment(
        num_rounds=500,
        agents_per_strategy=2,
        shading_alpha=0.8,
        seed=42,
    )

    assert set(result["results"]["auction_type"]) == {"second_price"}
    assert set(result["strategy_summary"]["strategy"]) == {
        "Truthful",
        "Shading (0.80×)",
        "Bandit",
    }
    assert result["proposition"]["truthful_expected_profit"] >= (
        result["proposition"]["shading_expected_profit"]
    )
    truthful = result["strategy_summary"].set_index("strategy").loc["Truthful"]
    assert truthful["avg_bid_to_value"] == pytest.approx(1.0)


def test_vickrey_experiment_rejects_too_many_agents():
    with pytest.raises(ValueError):
        run_vickrey_dominance_experiment(agents_per_strategy=6)
