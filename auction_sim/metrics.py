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
        )
        .reset_index()
        .sort_values("total_profit", ascending=False)
    )

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
    }