import pandas as pd

from auction_sim.results import AuctionResult


def results_to_dataframe(results: list[AuctionResult]) -> pd.DataFrame:
    """
    Converts simulation results into one row per agent per auction round.

    This makes later analysis much easier.
    """

    rows = []

    for result in results:
        for agent_id in result.bids:
            rows.append(
                {
                    "round_id": result.round_id,
                    "auction_type": result.auction_type,
                    "agent_id": agent_id,
                    "valuation": result.valuations[agent_id],
                    "bid": result.bids[agent_id],
                    "profit": result.profits[agent_id],
                    "is_winner": agent_id == result.winner_id,
                    "price_paid": result.price_paid if agent_id == result.winner_id else 0.0,
                    "seller_revenue": result.seller_revenue,
                    "winner_id": result.winner_id,
                }
            )

    return pd.DataFrame(rows)