import pytest
import pandas as pd

from auction_sim.revenue_equality import (
    _holm_pairwise_comparisons,
    _repeated_measures_anova,
    run_revenue_equality_experiment,
)


def test_revenue_equality_records_each_trial_for_all_formats():
    result = run_revenue_equality_experiment(
        num_rounds=500,
        bidder_count=8,
        seed=42,
    )

    revenues = result["revenue_by_trial"]
    assert len(revenues) == 2_000
    assert set(revenues["auction_format"]) == {
        "First price",
        "Second price",
        "English",
        "Dutch",
    }
    assert revenues.groupby("auction_format")["round_id"].nunique().eq(500).all()
    assert len(result["format_summary"]) == 4


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
    assert comparison["english_average_revenue"] == pytest.approx(
        comparison["second_price_average_revenue"]
    )
    assert comparison["dutch_average_revenue"] == pytest.approx(
        comparison["first_price_average_revenue"]
    )
    anova = comparison["repeated_measures_anova"]
    assert anova["format_degrees_of_freedom"] == 3
    assert anova["error_degrees_of_freedom"] == 5_997
    assert "repeated-measures ANOVA" in comparison["interpretation"]
    if anova["null_hypothesis_rejected"]:
        assert len(comparison["pairwise_comparisons"]) == 6
        assert all(
            "holm_adjusted_p_value" in pair
            for pair in comparison["pairwise_comparisons"]
        )


def test_theoretical_formats_match_equivalent_formats_trial_by_trial():
    result = run_revenue_equality_experiment(
        num_rounds=200,
        bidder_count=8,
        seed=42,
    )
    revenues = result["revenue_by_trial"].pivot(
        index="round_id",
        columns="auction_format",
        values="seller_revenue",
    )

    assert revenues["English"].equals(revenues["Second price"])
    assert revenues["Dutch"].equals(revenues["First price"])


def test_repeated_measures_anova_and_holm_detect_format_difference():
    revenues = pd.DataFrame(
        {
            "A": [10, 20, 30, 40, 50, 60],
            "B": [10, 20, 30, 40, 50, 60],
            "C": [15, 25, 35, 45, 55, 65],
        }
    )

    anova = _repeated_measures_anova(revenues)
    comparisons = _holm_pairwise_comparisons(revenues)

    assert anova["null_hypothesis_rejected"] is True
    significant_pairs = {
        frozenset((pair["first_format"], pair["second_format"]))
        for pair in comparisons
        if pair["significant"]
    }
    assert significant_pairs == {
        frozenset(("A", "C")),
        frozenset(("B", "C")),
    }


def test_revenue_equality_requires_multiple_bidders():
    with pytest.raises(ValueError):
        run_revenue_equality_experiment(bidder_count=1)
