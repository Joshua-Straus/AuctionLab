from __future__ import annotations

import pandas as pd

from market_sim.market import MarketResult


def _maximum_feasible_surplus(result: MarketResult) -> float:
    buyer_values = sorted(result.buyer_values.values(), reverse=True)
    seller_costs = sorted(result.seller_costs.values())
    return sum(
        max(0.0, value - cost)
        for value, cost in zip(buyer_values, seller_costs)
        if value >= cost
    )


def market_results_to_dataframe(
    results: list[MarketResult],
) -> pd.DataFrame:
    rows = []
    for result in results:
        buyer_trades = {trade.buyer_id: trade for trade in result.trades}
        seller_trades = {trade.seller_id: trade for trade in result.trades}
        realized_surplus = sum(
            trade.buyer_value - trade.seller_cost for trade in result.trades
        )
        maximum_surplus = _maximum_feasible_surplus(result)
        efficiency = (
            realized_surplus / maximum_surplus
            if maximum_surplus > 0
            else 1.0
        )
        trade_volume = len(result.trades)
        average_price = (
            sum(trade.price for trade in result.trades) / trade_volume
            if trade_volume
            else 0.0
        )
        average_spread = (
            sum(
                trade.buyer_bid - trade.seller_ask
                for trade in result.trades
            )
            / trade_volume
            if trade_volume
            else 0.0
        )

        round_fields = {
            "trade_volume": trade_volume,
            "buyer_surplus": sum(
                trade.buyer_profit for trade in result.trades
            ),
            "seller_surplus": sum(
                trade.seller_profit for trade in result.trades
            ),
            "total_surplus": realized_surplus,
            "maximum_feasible_surplus": maximum_surplus,
            "allocative_efficiency": efficiency,
            "avg_transaction_price": average_price,
            "avg_bid_ask_spread": average_spread,
            "unmatched_buyers": len(result.buyer_values) - trade_volume,
            "unmatched_sellers": len(result.seller_costs) - trade_volume,
        }

        for agent_id, value in result.buyer_values.items():
            trade = buyer_trades.get(agent_id)
            rows.append(
                {
                    "round_id": result.round_id,
                    "agent_id": agent_id,
                    "role": "buyer",
                    "private_value": value,
                    "order": result.buyer_bids[agent_id],
                    "matched": trade is not None,
                    "transaction_price": trade.price if trade else 0.0,
                    "profit": trade.buyer_profit if trade else 0.0,
                    **round_fields,
                }
            )
        for agent_id, cost in result.seller_costs.items():
            trade = seller_trades.get(agent_id)
            rows.append(
                {
                    "round_id": result.round_id,
                    "agent_id": agent_id,
                    "role": "seller",
                    "private_value": cost,
                    "order": result.seller_asks[agent_id],
                    "matched": trade is not None,
                    "transaction_price": trade.price if trade else 0.0,
                    "profit": trade.seller_profit if trade else 0.0,
                    **round_fields,
                }
            )

    return pd.DataFrame(rows)
