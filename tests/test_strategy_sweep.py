from auction_sim.experiments import run_strategy_sweep


def test_strategy_sweep_returns_one_row_per_alpha(tmp_path):
    summary = run_strategy_sweep(
        alpha_values=[0.6, 0.8, 1.0],
        num_rounds=50,
        num_agents_per_alpha=2,
        output_dir=str(tmp_path),
    )

    assert summary["alpha"].tolist() == [0.6, 0.8, 1.0]
    assert len(summary) == 3


def test_strategy_sweep_contains_strategy_metrics(tmp_path):
    summary = run_strategy_sweep(
        alpha_values=[0.7, 0.9],
        num_rounds=25,
        num_agents_per_alpha=2,
        output_dir=str(tmp_path),
    )

    expected = {
        "alpha",
        "num_agents",
        "total_profit",
        "avg_profit",
        "win_rate",
        "avg_regret",
        "avg_profit_when_winner",
        "avg_seller_revenue",
        "allocative_efficiency",
    }
    assert expected.issubset(summary.columns)


def test_strategy_sweep_saves_csv_and_plots(tmp_path):
    run_strategy_sweep(
        alpha_values=[0.8, 1.0],
        num_rounds=20,
        num_agents_per_alpha=1,
        output_dir=str(tmp_path),
    )

    assert (tmp_path / "strategy_sweep.csv").exists()
    assert (tmp_path / "strategy_avg_profit.png").exists()
    assert (tmp_path / "strategy_win_rate.png").exists()
