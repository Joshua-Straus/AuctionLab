"""
File to compute various metrics and summaries from auction simulation results.
"""

import pandas as pd


def summarize_agents(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes basic performance metrics for each agent.
    """

    summary = (
        df.groupby("agent_id")
        .agg(
            total_profit=("profit", "sum"),
            avg_profit=("profit", "mean"),
            win_rate=("is_winner", "mean"),
            avg_bid=("bid", "mean"),
            avg_valuation=("valuation", "mean"),
            total_spent=("price_paid", "sum"),
            avg_regret=("regret", "mean"),
            total_regret=("regret", "sum"),
        )
        .reset_index()
    )

    avg_profit_when_winner = (
        df[df["is_winner"]]
        .groupby("agent_id")["profit"]
        .mean()
        .rename("avg_profit_when_winner")
        .reset_index()
    )

    summary = summary.merge(
        avg_profit_when_winner,
        on="agent_id",
        how="left",
    )
    summary["avg_profit_when_winner"] = summary[
        "avg_profit_when_winner"
    ].fillna(0.0)
    summary = summary.sort_values("total_profit", ascending=False)

    return summary


def summarize_auction(df: pd.DataFrame) -> dict:
    """
    Computes auction-level summary metrics.
    """

    num_rounds = df["round_id"].nunique()

    round_level = df.drop_duplicates("round_id")

    return {
        "num_rounds": num_rounds,
        "auction_type": df["auction_type"].iloc[0],
        "avg_seller_revenue": round_level["seller_revenue"].mean(),
        "total_seller_revenue": round_level["seller_revenue"].sum(),
        "avg_winning_price": round_level["seller_revenue"].mean(),
        "allocative_efficiency": round_level["is_efficient_round"].mean(),
        "avg_price_to_winner_value": round_level["price_to_winner_value"].mean(),
        "avg_winner_valuation": round_level["winner_valuation"].mean(),
    }
