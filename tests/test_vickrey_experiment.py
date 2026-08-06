import pytest

from auction_sim.vickrey import run_vickrey_dominance_experiment


def test_vickrey_experiment_compares_nearby_bids_under_same_conditions():
    result = run_vickrey_dominance_experiment(
        num_rounds=200,
        bidder_count=5,
        bid_spread=20.0,
        bid_count=9,
        seed=42,
    )

    assert set(result["results"]["auction_type"]) == {"second_price"}
    assert len(result["strategy_summary"]) == 9
    assert result["strategy_summary"]["bid_delta"].tolist() == pytest.approx(
        [-20, -15, -10, -5, 0, 5, 10, 15, 20]
    )
    assert result["proposition"]["truthful_losses"] == 0
    assert result["proposition"]["supports_proposition"] is True


def test_truthful_bid_ties_itself_in_every_round():
    result = run_vickrey_dominance_experiment(num_rounds=50, seed=42)

    truthful_row = result["strategy_summary"].query("bid_delta == 0").iloc[0]
    assert truthful_row["ties"] == 50
    assert truthful_row["truthful_wins"] == 0
    assert truthful_row["truthful_losses"] == 0


def test_vickrey_experiment_counts_every_nontruthful_comparison():
    result = run_vickrey_dominance_experiment(
        num_rounds=25,
        bid_count=7,
        seed=42,
    )

    assert result["proposition"]["total_comparisons"] == 25 * 6


def test_vickrey_experiment_requires_odd_bid_count():
    with pytest.raises(ValueError):
        run_vickrey_dominance_experiment(bid_count=4)
