import pytest

from auction_sim.auctions import (
    DutchAuction,
    EnglishAuction,
    FirstPriceAuction,
    SecondPriceAuction,
    TheoreticalDutchAuction,
    TheoreticalEnglishAuction,
)


def test_first_price_auction_type():
    auction = FirstPriceAuction()

    assert auction.auction_type == "first_price"


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


def test_english_auction_uses_one_hundred_equal_bid_increments():
    auction = EnglishAuction(min_bid=20.0, max_bid=120.0)

    assert auction.bid_increment == pytest.approx(1.0)


def test_english_auction_starts_at_minimum_bid_for_single_bidder():
    auction = EnglishAuction(min_bid=20.0, max_bid=120.0)
    result = auction.run(
        round_id=1,
        valuations={"a": 80.0},
        bids={"a": 80.0},
    )

    assert result.winner_id == "a"
    assert result.price_paid == pytest.approx(20.0)


def test_english_auction_winner_pays_second_highest_bid():
    auction = EnglishAuction(min_bid=20.0, max_bid=120.0)
    result = auction.run(
        round_id=1,
        valuations={"a": 100.0, "b": 80.0, "c": 60.0},
        bids={"a": 95.5, "b": 79.5, "c": 55.0},
    )

    assert result.winner_id == "a"
    assert result.price_paid == pytest.approx(79.5)
    assert result.profits["a"] == pytest.approx(20.5)


def test_english_auction_rejects_empty_bid_range():
    with pytest.raises(ValueError):
        EnglishAuction(min_bid=50.0, max_bid=50.0)


def test_dutch_auction_uses_one_hundred_equal_bid_decrements():
    auction = DutchAuction(min_bid=20.0, max_bid=120.0)

    assert auction.bid_decrement == pytest.approx(1.0)


def test_dutch_auction_starts_at_maximum_bid():
    auction = DutchAuction(min_bid=20.0, max_bid=120.0)
    result = auction.run(
        round_id=1,
        valuations={"a": 120.0, "b": 80.0},
        bids={"a": 120.0, "b": 80.0},
    )

    assert result.winner_id == "a"
    assert result.price_paid == pytest.approx(120.0)


def test_dutch_auction_stops_at_first_acceptable_decrement():
    auction = DutchAuction(min_bid=20.0, max_bid=120.0)
    result = auction.run(
        round_id=1,
        valuations={"a": 100.0, "b": 80.0, "c": 60.0},
        bids={"a": 95.5, "b": 79.5, "c": 55.0},
    )

    assert result.winner_id == "a"
    assert result.price_paid == pytest.approx(95.0)
    assert result.profits["a"] == pytest.approx(5.0)


def test_dutch_auction_rejects_empty_bid_range():
    with pytest.raises(ValueError):
        DutchAuction(min_bid=50.0, max_bid=50.0)


def test_theoretical_english_auction_settles_at_second_highest_value():
    auction = TheoreticalEnglishAuction()
    result = auction.run(
        round_id=1,
        valuations={"a": 90.0, "b": 72.5, "c": 40.0},
        bids={"a": 90.0, "b": 72.5, "c": 40.0},
    )

    assert result.winner_id == "a"
    assert result.price_paid == pytest.approx(72.5)


def test_theoretical_dutch_auction_settles_at_exact_highest_stop():
    auction = TheoreticalDutchAuction()
    result = auction.run(
        round_id=1,
        valuations={"a": 91.0, "b": 80.0, "c": 30.0},
        bids={"a": 60.6666666667, "b": 53.3333333333, "c": 20.0},
    )

    assert result.winner_id == "a"
    assert result.price_paid == pytest.approx(60.6666666667)


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
