"""
File to handle plotting of auction results.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def plot_agent_profit(
    agent_summary: pd.DataFrame,
    output_path: str,
) -> None:
    """
    Saves a bar chart of total profit by agent.
    """

    Path(output_path).parent.mkdir(exist_ok=True)

    sorted_summary = agent_summary.sort_values("total_profit", ascending=True)

    plt.figure(figsize=(8, 5))
    plt.barh(sorted_summary["agent_id"], sorted_summary["total_profit"])
    plt.xlabel("Total Profit")
    plt.ylabel("Agent")
    plt.title("Total Profit by Agent")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_agent_win_rate(
    agent_summary: pd.DataFrame,
    output_path: str,
) -> None:
    """
    Saves a bar chart of win rate by agent.
    """

    Path(output_path).parent.mkdir(exist_ok=True)

    sorted_summary = agent_summary.sort_values("win_rate", ascending=True)

    plt.figure(figsize=(8, 5))
    plt.barh(sorted_summary["agent_id"], sorted_summary["win_rate"])
    plt.xlabel("Win Rate")
    plt.ylabel("Agent")
    plt.title("Win Rate by Agent")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_strategy_profit(
    strategy_summary: pd.DataFrame,
    output_path: str,
) -> None:
    """Saves average profit by shading factor."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    sorted_summary = strategy_summary.sort_values("alpha")
    plt.figure(figsize=(8, 5))
    plt.plot(
        sorted_summary["alpha"],
        sorted_summary["avg_profit"],
        marker="o",
    )
    plt.xlabel("Bid multiplier (alpha)")
    plt.ylabel("Average profit per round")
    plt.title("Average Profit by Bidding Strategy")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_strategy_win_rate(
    strategy_summary: pd.DataFrame,
    output_path: str,
) -> None:
    """Saves average win rate by shading factor."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    sorted_summary = strategy_summary.sort_values("alpha")
    plt.figure(figsize=(8, 5))
    plt.plot(
        sorted_summary["alpha"],
        sorted_summary["win_rate"],
        marker="o",
    )
    plt.xlabel("Bid multiplier (alpha)")
    plt.ylabel("Win rate")
    plt.title("Win Rate by Bidding Strategy")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_competition_revenue(
    competition_summary: pd.DataFrame,
    output_path: str,
) -> None:
    """Saves average seller revenue by bidder count."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    sorted_summary = competition_summary.sort_values("num_agents")
    plt.figure(figsize=(8, 5))
    plt.plot(
        sorted_summary["num_agents"],
        sorted_summary["avg_seller_revenue"],
        marker="o",
    )
    plt.xlabel("Number of bidders")
    plt.ylabel("Average seller revenue")
    plt.title("Seller Revenue by Competition Level")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
