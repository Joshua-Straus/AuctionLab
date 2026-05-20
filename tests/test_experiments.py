from auction_sim.auctions import FirstPriceAuction
from auction_sim.experiments import run_experiment


def test_run_experiment_returns_nonempty_results():
    df, agent_summary, auction_summary = run_experiment(
        auction=FirstPriceAuction(),
        num_rounds=100,
        seed=42,
    )

    assert not df.empty
    assert not agent_summary.empty
    assert auction_summary["num_rounds"] == 100


def test_run_experiment_has_expected_columns():
    df, agent_summary, auction_summary = run_experiment(
        auction=FirstPriceAuction(),
        num_rounds=100,
        seed=42,
    )

    expected_columns = {
        "round_id",
        "auction_type",
        "agent_id",
        "valuation",
        "bid",
        "profit",
        "is_winner",
        "price_paid",
        "seller_revenue",
        "winner_id",
    }

    assert expected_columns.issubset(set(df.columns))