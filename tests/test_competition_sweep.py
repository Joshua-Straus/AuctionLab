from auction_sim.experiments import (
    make_shading_competition_agents,
    run_competition_sweep,
)


def test_make_shading_competition_agents_creates_expected_number():
    agents = make_shading_competition_agents(num_agents=4, alpha=0.8)

    assert len(agents) == 4


def test_make_shading_competition_agents_uses_unique_ids():
    agents = make_shading_competition_agents(num_agents=4, alpha=0.8)
    agent_ids = [agent.agent_id for agent in agents]

    assert len(agent_ids) == len(set(agent_ids))


def test_make_shading_competition_agents_uses_alpha():
    agents = make_shading_competition_agents(num_agents=3, alpha=0.75)

    assert all(agent.alpha == 0.75 for agent in agents)


def test_run_competition_sweep_returns_one_row_per_bidder_count(tmp_path):
    df = run_competition_sweep(
        bidder_counts=[2, 4],
        num_rounds=50,
        output_dir=str(tmp_path),
    )

    assert len(df) == 2
    assert set(df["num_agents"]) == {2, 4}


def test_run_competition_sweep_has_expected_columns(tmp_path):
    df = run_competition_sweep(
        bidder_counts=[2],
        num_rounds=50,
        output_dir=str(tmp_path),
    )

    expected_columns = {
        "num_agents",
        "alpha",
        "auction_type",
        "num_rounds",
        "low_value",
        "high_value",
        "avg_seller_revenue",
        "total_seller_revenue",
        "avg_winning_price",
        "allocative_efficiency",
        "avg_price_to_winner_value",
        "avg_winner_valuation",
        "avg_agent_profit",
        "total_agent_profit",
    }

    assert expected_columns.issubset(set(df.columns))


def test_run_competition_sweep_saves_csv(tmp_path):
    run_competition_sweep(
        bidder_counts=[2],
        num_rounds=50,
        output_dir=str(tmp_path),
    )

    assert (tmp_path / "competition_sweep.csv").exists()
