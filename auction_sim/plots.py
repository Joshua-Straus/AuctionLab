"""
File to handle plotting of auction results.
"""

from pathlib import Path

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