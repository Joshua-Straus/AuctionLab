from auction_sim.auctions import FirstPriceAuction


def test_first_price_highest_bidder_wins():
    auction = FirstPriceAuction()

    valuations = {
        "a": 100,
        "b": 80,
        "c": 60,
    }

    bids = {
        "a": 50,
        "b": 70,
        "c": 40,
    }

    result = auction.run(
        round_id=0,
        valuations=valuations,
        bids=bids,
    )

    assert result.winner_id == "b"


def test_first_price_winner_pays_own_bid():
    auction = FirstPriceAuction()

    valuations = {
        "a": 100,
        "b": 80,
    }

    bids = {
        "a": 60,
        "b": 70,
    }

    result = auction.run(
        round_id=0,
        valuations=valuations,
        bids=bids,
    )

    assert result.winner_id == "b"
    assert result.price_paid == 70
    assert result.seller_revenue == 70


def test_first_price_profit_calculation():
    auction = FirstPriceAuction()

    valuations = {
        "a": 100,
        "b": 80,
    }

    bids = {
        "a": 60,
        "b": 70,
    }

    result = auction.run(
        round_id=0,
        valuations=valuations,
        bids=bids,
    )

    assert result.profits["b"] == 10
    assert result.profits["a"] == 0

from auction_sim.auctions import FirstPriceAuction, SecondPriceAuction


def test_second_price_highest_bidder_wins():
    auction = SecondPriceAuction()

    valuations = {
        "a": 100,
        "b": 80,
        "c": 60,
    }

    bids = {
        "a": 50,
        "b": 70,
        "c": 40,
    }

    result = auction.run(
        round_id=0,
        valuations=valuations,
        bids=bids,
    )

    assert result.winner_id == "b"


def test_second_price_winner_pays_second_highest_bid():
    auction = SecondPriceAuction()

    valuations = {
        "a": 100,
        "b": 80,
        "c": 60,
    }

    bids = {
        "a": 50,
        "b": 70,
        "c": 40,
    }

    result = auction.run(
        round_id=0,
        valuations=valuations,
        bids=bids,
    )

    assert result.winner_id == "b"
    assert result.price_paid == 50
    assert result.seller_revenue == 50


def test_second_price_profit_calculation():
    auction = SecondPriceAuction()

    valuations = {
        "a": 100,
        "b": 80,
        "c": 60,
    }

    bids = {
        "a": 50,
        "b": 70,
        "c": 40,
    }

    result = auction.run(
        round_id=0,
        valuations=valuations,
        bids=bids,
    )

    assert result.profits["b"] == 30
    assert result.profits["a"] == 0
    assert result.profits["c"] == 0