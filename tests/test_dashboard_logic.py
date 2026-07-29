import pytest

from dashboard_logic import (
    run_auction_dashboard,
    run_learning_dashboard,
)


def test_auction_dashboard_runner_returns_analytics():
    result = run_auction_dashboard(
        auction_type="first_price",
        num_rounds=20,
        bidder_count=4,
        strategy="mixed",
        alpha=0.8,
        low_value=0.0,
        high_value=100.0,
        seed=42,
    )

    assert not result["results"].empty
    assert result["auction_summary"]["num_rounds"] == 20


def test_dashboard_rejects_participant_counts_above_limit():
    with pytest.raises(ValueError):
        run_auction_dashboard(
            auction_type="first_price",
            num_rounds=20,
            bidder_count=17,
            strategy="truthful",
            alpha=0.8,
            low_value=0.0,
            high_value=100.0,
            seed=42,
        )


def test_learning_dashboard_returns_bandit_outputs():
    result = run_learning_dashboard(num_rounds=20, epsilon=0.1, seed=42)

    assert len(result["action_history"]) == 20
