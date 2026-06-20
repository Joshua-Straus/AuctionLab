from __future__ import annotations

import pandas as pd


def summarize_market_agents(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["agent_id", "role"], as_index=False)
        .agg(
            total_profit=("profit", "sum"),
            avg_profit=("profit", "mean"),
            trade_rate=("matched", "mean"),
            avg_order=("order", "mean"),
            avg_private_value=("private_value", "mean"),
            avg_transaction_price=("transaction_price", "mean"),
        )
        .sort_values("total_profit", ascending=False)
    )


def summarize_market(df: pd.DataFrame) -> dict:
    round_level = df.drop_duplicates("round_id")
    return {
        "num_rounds": int(df["round_id"].nunique()),
        "avg_trade_volume": round_level["trade_volume"].mean(),
        "total_trade_volume": int(round_level["trade_volume"].sum()),
        "avg_buyer_surplus": round_level["buyer_surplus"].mean(),
        "avg_seller_surplus": round_level["seller_surplus"].mean(),
        "avg_total_surplus": round_level["total_surplus"].mean(),
        "avg_transaction_price": round_level[
            "avg_transaction_price"
        ].mean(),
        "avg_bid_ask_spread": round_level["avg_bid_ask_spread"].mean(),
        "allocative_efficiency": round_level[
            "allocative_efficiency"
        ].mean(),
        "avg_unmatched_buyers": round_level["unmatched_buyers"].mean(),
        "avg_unmatched_sellers": round_level["unmatched_sellers"].mean(),
    }
