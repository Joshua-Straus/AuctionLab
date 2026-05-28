import pytest

from auction_sim.data import results_to_dataframe
from auction_sim.metrics import summarize_agents, summarize_auction
from auction_sim.results import AuctionResult


def make_metric_results() -> list[AuctionResult]:
    return [
        AuctionResult(
            round_id=1,
            auction_type="first_price",
            winner_id="a",
            price_paid=70.0,
            seller_revenue=70.0,
            valuations={"a": 100.0, "b": 90.0},
            bids={"a": 70.0, "b": 60.0},
            profits={"a": 30.0, "b": 0.0},
        ),
        AuctionResult(
            round_id=2,
            auction_type="first_price",
            winner_id="b",
            price_paid=95.0,
            seller_revenue=95.0,
            valuations={"a": 100.0, "b": 90.0},
            bids={"a": 80.0, "b": 95.0},
            profits={"a": 0.0, "b": -5.0},
        ),
    ]


def test_summarize_agents_includes_day_6_metrics():
    df = results_to_dataframe(make_metric_results())
    summary = summarize_agents(df)

    expected_columns = {
        "avg_regret",
        "total_regret",
        "avg_profit_when_winner",
    }

    assert expected_columns.issubset(summary.columns)


def test_summarize_agents_computes_regret_and_profit_when_winner():
    df = results_to_dataframe(make_metric_results())
    summary = summarize_agents(df).set_index("agent_id")

    assert summary.loc["a", "avg_regret"] == pytest.approx(2.5)
    assert summary.loc["a", "total_regret"] == pytest.approx(5.0)
    assert summary.loc["a", "avg_profit_when_winner"] == pytest.approx(30.0)

    assert summary.loc["b", "avg_regret"] == pytest.approx(10.0)
    assert summary.loc["b", "total_regret"] == pytest.approx(20.0)
    assert summary.loc["b", "avg_profit_when_winner"] == pytest.approx(-5.0)


def test_summarize_auction_includes_day_6_metrics():
    df = results_to_dataframe(make_metric_results())
    summary = summarize_auction(df)

    expected_keys = {
        "allocative_efficiency",
        "avg_price_to_winner_value",
        "avg_winner_valuation",
    }

    assert expected_keys.issubset(summary)


def test_summarize_auction_computes_round_level_day_6_metrics():
    df = results_to_dataframe(make_metric_results())
    summary = summarize_auction(df)

    assert summary["num_rounds"] == 2
    assert summary["allocative_efficiency"] == pytest.approx(0.5)
    assert summary["avg_price_to_winner_value"] == pytest.approx(
        ((70.0 / 100.0) + (95.0 / 90.0)) / 2
    )
    assert summary["avg_winner_valuation"] == pytest.approx(95.0)
