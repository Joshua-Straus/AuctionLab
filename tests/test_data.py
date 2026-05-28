import pytest

from auction_sim.data import results_to_dataframe
from auction_sim.results import AuctionResult


def make_result(
    *,
    round_id: int = 1,
    winner_id: str = "a",
    price_paid: float = 80.0,
    valuations: dict[str, float] | None = None,
    bids: dict[str, float] | None = None,
) -> AuctionResult:
    valuations = valuations or {
        "a": 100.0,
        "b": 90.0,
        "c": 70.0,
    }
    bids = bids or {
        "a": 100.0,
        "b": 80.0,
        "c": 60.0,
    }
    profits = {
        agent_id: valuations[agent_id] - price_paid
        if agent_id == winner_id
        else 0.0
        for agent_id in valuations
    }

    return AuctionResult(
        round_id=round_id,
        auction_type="second_price",
        winner_id=winner_id,
        price_paid=price_paid,
        seller_revenue=price_paid,
        valuations=valuations,
        bids=bids,
        profits=profits,
    )


def test_results_to_dataframe_adds_day_6_columns():
    df = results_to_dataframe([make_result()])

    expected_columns = {
        "highest_value_agent",
        "is_highest_value_agent",
        "is_efficient_round",
        "winner_valuation",
        "price_to_winner_value",
        "regret",
    }

    assert expected_columns.issubset(df.columns)


def test_results_to_dataframe_marks_efficient_round():
    df = results_to_dataframe([make_result()])

    assert df["highest_value_agent"].unique().tolist() == ["a"]
    assert df["is_efficient_round"].unique().tolist() == [True]
    assert df.loc[df["agent_id"] == "a", "is_highest_value_agent"].item() is True


def test_results_to_dataframe_marks_inefficient_round():
    result = make_result(
        winner_id="b",
        price_paid=95.0,
        valuations={
            "a": 100.0,
            "b": 90.0,
            "c": 70.0,
        },
        bids={
            "a": 80.0,
            "b": 95.0,
            "c": 60.0,
        },
    )

    df = results_to_dataframe([result])

    assert df["highest_value_agent"].unique().tolist() == ["a"]
    assert df["is_efficient_round"].unique().tolist() == [False]


def test_results_to_dataframe_computes_winner_value_ratio():
    df = results_to_dataframe([make_result(price_paid=80.0)])

    assert df["winner_valuation"].unique().tolist() == [100.0]
    assert df["price_to_winner_value"].unique().item() == pytest.approx(0.8)


def test_results_to_dataframe_sets_zero_ratio_for_zero_winner_value():
    result = make_result(
        winner_id="a",
        price_paid=0.0,
        valuations={
            "a": 0.0,
            "b": 0.0,
        },
        bids={
            "a": 0.0,
            "b": 0.0,
        },
    )

    df = results_to_dataframe([result])

    assert df["price_to_winner_value"].unique().tolist() == [0.0]


def test_results_to_dataframe_computes_regret():
    df = results_to_dataframe([make_result(price_paid=80.0)])

    assert df.loc[df["agent_id"] == "a", "regret"].item() == 0.0
    assert df.loc[df["agent_id"] == "b", "regret"].item() == 10.0
    assert df.loc[df["agent_id"] == "c", "regret"].item() == 0.0
