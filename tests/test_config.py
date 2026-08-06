import pytest

from auction_sim.auctions import (
    DutchAuction,
    EnglishAuction,
    FirstPriceAuction,
    SecondPriceAuction,
)
from auction_sim.config import ExperimentConfig
from auction_sim.experiments import make_auction


def test_experiment_config_defaults():
    config = ExperimentConfig()

    assert config.auction_type == "first_price"
    assert config.num_rounds == 10_000
    assert config.low_value == 0.0
    assert config.high_value == 100.0
    assert config.seed == 42
    assert config.output_dir == "outputs"


def test_experiment_config_num_rounds():
    config = ExperimentConfig(num_rounds=100)

    assert config.num_rounds == 100


def test_make_first_price_auction():
    auction = make_auction("first_price")

    assert isinstance(auction, FirstPriceAuction)


def test_make_second_price_auction():
    auction = make_auction("second_price")

    assert isinstance(auction, SecondPriceAuction)


def test_make_english_auction_with_bid_bounds():
    auction = make_auction("english", min_bid=20.0, max_bid=120.0)

    assert isinstance(auction, EnglishAuction)
    assert auction.min_bid == 20.0
    assert auction.max_bid == 120.0


def test_make_dutch_auction_with_bid_bounds():
    auction = make_auction("dutch", min_bid=20.0, max_bid=120.0)

    assert isinstance(auction, DutchAuction)
    assert auction.min_bid == 20.0
    assert auction.max_bid == 120.0


def test_make_unknown_auction_raises_error():
    with pytest.raises(ValueError):
        make_auction("bad_auction")
