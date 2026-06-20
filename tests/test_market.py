import pytest

from market_sim.market import DoubleAuction, MarketResult, Trade


def test_double_auction_matches_crossing_orders_at_midpoint():
    result = DoubleAuction().run(
        round_id=1,
        buyer_valuations={"buyer": 100.0},
        seller_valuations={"seller": 40.0},
        buyer_bids={"buyer": 90.0},
        seller_asks={"seller": 50.0},
    )

    assert isinstance(result, MarketResult)
    assert len(result.trades) == 1

    trade = result.trades[0]
    assert isinstance(trade, Trade)
    assert trade.buyer_id == "buyer"
    assert trade.seller_id == "seller"
    assert trade.price == pytest.approx(70.0)
    assert trade.buyer_profit == pytest.approx(30.0)
    assert trade.seller_profit == pytest.approx(30.0)


def test_double_auction_matches_orders_by_price_priority():
    result = DoubleAuction().run(
        round_id=2,
        buyer_valuations={"b1": 110.0, "b2": 95.0, "b3": 60.0},
        seller_valuations={"s1": 30.0, "s2": 70.0, "s3": 90.0},
        buyer_bids={"b1": 100.0, "b2": 90.0, "b3": 55.0},
        seller_asks={"s1": 40.0, "s2": 80.0, "s3": 95.0},
    )

    assert [(trade.buyer_id, trade.seller_id) for trade in result.trades] == [
        ("b1", "s1"),
        ("b2", "s2"),
    ]


def test_double_auction_returns_no_trades_when_orders_do_not_cross():
    result = DoubleAuction().run(
        round_id=3,
        buyer_valuations={"buyer": 50.0},
        seller_valuations={"seller": 70.0},
        buyer_bids={"buyer": 45.0},
        seller_asks={"seller": 75.0},
    )

    assert result.trades == []


def test_double_auction_profit_uses_private_values_not_submitted_orders():
    result = DoubleAuction().run(
        round_id=4,
        buyer_valuations={"buyer": 120.0},
        seller_valuations={"seller": 20.0},
        buyer_bids={"buyer": 80.0},
        seller_asks={"seller": 60.0},
    )

    trade = result.trades[0]
    assert trade.price == pytest.approx(70.0)
    assert trade.buyer_profit == pytest.approx(50.0)
    assert trade.seller_profit == pytest.approx(50.0)


def test_double_auction_result_keeps_round_and_order_books():
    result = DoubleAuction().run(
        round_id=5,
        buyer_valuations={"buyer": 100.0},
        seller_valuations={"seller": 40.0},
        buyer_bids={"buyer": 90.0},
        seller_asks={"seller": 50.0},
    )

    assert result.round_id == 5
    assert result.buyer_bids == {"buyer": 90.0}
    assert result.seller_asks == {"seller": 50.0}


def test_double_auction_requires_submitted_orders():
    with pytest.raises(ValueError):
        DoubleAuction().run(
            round_id=1,
            buyer_valuations={"buyer": 100.0},
            seller_valuations={"seller": 40.0},
        )


def test_double_auction_rejects_mismatched_agent_ids():
    with pytest.raises(ValueError):
        DoubleAuction().run(
            round_id=1,
            buyer_valuations={"buyer": 100.0},
            seller_valuations={"seller": 40.0},
            buyer_bids={"other_buyer": 90.0},
            seller_asks={"seller": 50.0},
        )
