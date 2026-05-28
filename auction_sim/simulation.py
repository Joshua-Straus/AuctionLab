"""
File to define the main Simulation class that runs the auction simulations.
"""

from __future__ import annotations

import random

from auction_sim.agents import Agent
from auction_sim.auctions import Auction
from auction_sim.results import AuctionResult


class Simulation:
    def __init__(
        self,
        auction: Auction,
        low_value: float = 0,
        high_value: float = 100,
        num_rounds: int = 100,
        agents: list[Agent] | None = None,
        seed: int | None = None,
    ):
        self.auction = auction
        self.low_value = low_value
        self.high_value = high_value
        self.agents = agents or []
        self.num_rounds = num_rounds
        if seed is not None:
            random.seed(seed)

    def run(self) -> list[AuctionResult]:
        records = []
        for round_id in range(1, self.num_rounds + 1):
            valuations = {}
            bids = {}
            for agent in self.agents:
                valuation = random.uniform(self.low_value, self.high_value)
                bid = agent.bid(
                    valuation,
                    context={
                        "round_id": round_id,
                        "auction_type": self.auction.auction_type,
                    },
                )
                valuations[agent.agent_id] = valuation
                bids[agent.agent_id] = bid

            result = self.auction.run(
                round_id=round_id,
                valuations=valuations,
                bids=bids,
            )
                
            for agent in self.agents:
                agent.update(
                    {
                        "round_id": round_id,
                        "auction_type": self.auction.auction_type,
                        "valuation": valuations[agent.agent_id],
                        "bid": bids[agent.agent_id],
                        "profit": result.profits[agent.agent_id],
                        "winner_id": result.winner_id,
                        "price_paid": result.price_paid,
                    }
                ) 
            records.append(result)
        return records
