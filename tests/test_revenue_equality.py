import pytest

from auction_sim.revenue_equality import run_revenue_equality_experiment


def test_revenue_equality_records_each_trial_for_both_formats():
    result = run_revenue_equality_experiment(
        num_rounds=500,
        bidder_count=8,
        seed=42,
    )

    revenues = result["revenue_by_trial"]
    assert len(revenues) == 1_000
    assert set(revenues["auction_format"]) == {"First price", "Second price"}
    assert revenues.groupby("auction_format")["round_id"].nunique().eq(500).all()
    assert len(result["format_summary"]) == 2


def test_revenue_equality_averages_are_close_for_large_trial():
    result = run_revenue_equality_experiment(
        num_rounds=2_000,
        bidder_count=8,
        seed=42,
    )

    comparison = result["comparison"]
    assert comparison["first_price_average_revenue"] == pytest.approx(
        comparison["second_price_average_revenue"], rel=0.02
    )
    assert comparison["consistent_with_revenue_equality"]


def test_revenue_equality_requires_multiple_bidders():
    with pytest.raises(ValueError):
        run_revenue_equality_experiment(bidder_count=1)
