"""
File to handle display and visualization of auction results.
"""

import pandas as pd

from auction_sim.results import AuctionResult


def print_auction_result(result: AuctionResult) -> None:
    print(f"Round {result.round_id}")
    print(f"Auction type: {result.auction_type}")
    print(f"Winner: {result.winner_id}")
    print(f"Price paid: {result.price_paid:.2f}")
    print(f"Seller revenue: {result.seller_revenue:.2f}")

    print("Bids:")
    for agent_id, bid in result.bids.items():
        value = result.valuations[agent_id]
        profit = result.profits[agent_id]
        print(
            f"  {agent_id}: "
            f"value={value:.2f}, "
            f"bid={bid:.2f}, "
            f"profit={profit:.2f}"
        )

    print("-" * 50)


def print_experiment_summary(
    auction_name: str,
    auction_summary: dict,
    agent_summary: pd.DataFrame,
) -> None:
    print("\n" + "=" * 80)
    print(f"Auction: {auction_name}")
    print("=" * 80)

    print("\nAuction Summary")
    print("-" * 80)
    for key, value in auction_summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

    print("\nAgent Summary")
    print("-" * 80)

    display_cols = [
        "agent_id",
        "total_profit",
        "avg_profit",
        "win_rate",
        "avg_bid",
        "avg_valuation",
        "total_spent",
        "avg_regret",
        "total_regret",
        "avg_profit_when_winner",
    ]

    existing_cols = [col for col in display_cols if col in agent_summary.columns]

    print(agent_summary[existing_cols].to_string(index=False))
