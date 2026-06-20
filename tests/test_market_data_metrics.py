import pytest

from market_sim.data import market_results_to_dataframe
from market_sim.market import DoubleAuction
from market_sim.metrics import summarize_market, summarize_market_agents


def test_market_dataframe_and_metrics_for_single_trade():
    result = DoubleAuction().run(
        round_id=1,
        buyer_valuations={"buyer": 100.0},
        seller_valuations={"seller": 20.0},
        buyer_bids={"buyer": 90.0},
        seller_asks={"seller": 30.0},
    )

    df = market_results_to_dataframe([result])
    summary = summarize_market(df)
    agents = summarize_market_agents(df)

    assert len(df) == 2
    assert summary["total_trade_volume"] == 1
    assert summary["avg_total_surplus"] == pytest.approx(80.0)
    assert summary["allocative_efficiency"] == pytest.approx(1.0)
    assert set(agents["role"]) == {"buyer", "seller"}


def test_market_efficiency_detects_inefficient_no_trade():
    result = DoubleAuction().run(
        round_id=1,
        buyer_valuations={"buyer": 100.0},
        seller_valuations={"seller": 20.0},
        buyer_bids={"buyer": 10.0},
        seller_asks={"seller": 90.0},
    )

    df = market_results_to_dataframe([result])
    summary = summarize_market(df)

    assert summary["total_trade_volume"] == 0
    assert summary["allocative_efficiency"] == 0.0


def test_market_efficiency_is_one_when_no_gains_are_feasible():
    result = DoubleAuction().run(
        round_id=1,
        buyer_valuations={"buyer": 20.0},
        seller_valuations={"seller": 80.0},
        buyer_bids={"buyer": 20.0},
        seller_asks={"seller": 80.0},
    )

    df = market_results_to_dataframe([result])

    assert summarize_market(df)["allocative_efficiency"] == 1.0


def test_market_dataframe_counts_unmatched_participants():
    result = DoubleAuction().run(
        round_id=1,
        buyer_valuations={"b1": 100.0, "b2": 50.0},
        seller_valuations={"s1": 20.0, "s2": 90.0},
        buyer_bids={"b1": 90.0, "b2": 40.0},
        seller_asks={"s1": 30.0, "s2": 95.0},
    )

    df = market_results_to_dataframe([result])
    round_row = df.iloc[0]

    assert round_row["trade_volume"] == 1
    assert round_row["unmatched_buyers"] == 1
    assert round_row["unmatched_sellers"] == 1
