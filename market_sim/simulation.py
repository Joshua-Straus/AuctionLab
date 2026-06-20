from __future__ import annotations

import random

from market_sim.market import DoubleAuction, MarketResult
from market_sim.market_agents import BuyerAgent, SellerAgent


class MarketSimulation:
    def __init__(
        self,
        buyers: list[BuyerAgent],
        sellers: list[SellerAgent],
        num_rounds: int = 1_000,
        buyer_value_low: float = 0.0,
        buyer_value_high: float = 100.0,
        seller_cost_low: float = 0.0,
        seller_cost_high: float = 100.0,
        seed: int | None = 42,
        market: DoubleAuction | None = None,
    ):
        if not buyers or not sellers:
            raise ValueError("Market simulation requires buyers and sellers.")
        if num_rounds <= 0:
            raise ValueError("num_rounds must be positive.")
        if buyer_value_low > buyer_value_high:
            raise ValueError("Buyer value range is invalid.")
        if seller_cost_low > seller_cost_high:
            raise ValueError("Seller cost range is invalid.")

        self.buyers = buyers
        self.sellers = sellers
        self.num_rounds = num_rounds
        self.buyer_value_low = buyer_value_low
        self.buyer_value_high = buyer_value_high
        self.seller_cost_low = seller_cost_low
        self.seller_cost_high = seller_cost_high
        self.market = market or DoubleAuction()
        self.rng = random.Random(seed)

    def run(self) -> list[MarketResult]:
        results = []
        for round_id in range(1, self.num_rounds + 1):
            buyer_values = {
                buyer.agent_id: self.rng.uniform(
                    self.buyer_value_low,
                    self.buyer_value_high,
                )
                for buyer in self.buyers
            }
            seller_costs = {
                seller.agent_id: self.rng.uniform(
                    self.seller_cost_low,
                    self.seller_cost_high,
                )
                for seller in self.sellers
            }
            context = {"round_id": round_id, "market_type": "double_auction"}
            buyer_bids = {
                buyer.agent_id: buyer.bid(
                    buyer_values[buyer.agent_id],
                    context=context,
                )
                for buyer in self.buyers
            }
            seller_asks = {
                seller.agent_id: seller.ask(
                    seller_costs[seller.agent_id],
                    context=context,
                )
                for seller in self.sellers
            }

            result = self.market.run(
                round_id=round_id,
                buyer_valuations=buyer_values,
                seller_valuations=seller_costs,
                buyer_bids=buyer_bids,
                seller_asks=seller_asks,
            )
            buyer_trades = {trade.buyer_id: trade for trade in result.trades}
            seller_trades = {trade.seller_id: trade for trade in result.trades}

            for buyer in self.buyers:
                trade = buyer_trades.get(buyer.agent_id)
                buyer.update(
                    {
                        "round_id": round_id,
                        "role": "buyer",
                        "value": buyer_values[buyer.agent_id],
                        "order": buyer_bids[buyer.agent_id],
                        "traded": trade is not None,
                        "price": trade.price if trade else 0.0,
                        "profit": trade.buyer_profit if trade else 0.0,
                    }
                )
            for seller in self.sellers:
                trade = seller_trades.get(seller.agent_id)
                seller.update(
                    {
                        "round_id": round_id,
                        "role": "seller",
                        "cost": seller_costs[seller.agent_id],
                        "order": seller_asks[seller.agent_id],
                        "traded": trade is not None,
                        "price": trade.price if trade else 0.0,
                        "profit": trade.seller_profit if trade else 0.0,
                    }
                )
            results.append(result)

        return results
