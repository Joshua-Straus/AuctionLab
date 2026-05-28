"""
File to handle data processing for auction simulation results.
"""

import pandas as pd

from auction_sim.results import AuctionResult


def results_to_dataframe(results: list[AuctionResult]) -> pd.DataFrame:
    """
    Converts simulation results into one row per agent per auction round.

    This makes later analysis much easier.
    """

    rows = []

    for result in results:
        highest_value = max(result.valuations.values())
        highest_value_agent = [
            agent_id
            for agent_id, value in result.valuations.items()
            if value == highest_value
        ][0]

        winner_valuation = result.valuations[result.winner_id]
        price_to_winner_value = (
            result.price_paid / winner_valuation
            if winner_valuation > 0
            else 0.0
        )
        is_efficient_round = result.winner_id == highest_value_agent

        for agent_id in result.bids:
            if agent_id == result.winner_id:
                regret = 0.0
            else:
                regret = max(0.0, result.valuations[agent_id] - result.price_paid)

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
                    "highest_value_agent": highest_value_agent,
                    "is_highest_value_agent": agent_id == highest_value_agent,
                    "is_efficient_round": is_efficient_round,
                    "winner_valuation": winner_valuation,
                    "price_to_winner_value": price_to_winner_value,
                    "regret": regret,
                }
            )

    return pd.DataFrame(rows)
