"""
File to define different auction mechanisms.
"""

from __future__ import annotations

import random
import heapq
from dataclasses import dataclass

from auction_sim.results import AuctionResult

@dataclass
class Auction:
    """
    Base class for auction mechanisms.
    """

    auction_type: str

    def run(
        self,
        round_id: int,
        valuations: dict[str, float],
        bids: dict[str, float],
    ) -> AuctionResult:
        raise NotImplementedError("Subclasses must implement run().")
    
@dataclass
class FirstPriceAuction(Auction):
    """
    First-price sealed-bid auction.
    """
    auction_type: str = "first_price"

    def run(
        self,
        round_id: int,
        valuations: dict[str, float],
        bids: dict[str, float],
    ) -> AuctionResult:
        if not bids:
            raise ValueError("Cannot run auction with no bids.")

        max_bid = max(bids.values())

        # Handle ties randomly among highest bidders.
        tied_winners = [
            agent_id for agent_id, bid in bids.items()
            if bid == max_bid
        ]
        winner_id = random.choice(tied_winners)
        price_paid = bids[winner_id]
        seller_revenue = price_paid
        
        profits = {}

        for agent_id, valuation in valuations.items():
            if agent_id == winner_id:
                profits[agent_id] = valuation - price_paid
            else:
                profits[agent_id] = 0.0
        
        return AuctionResult(
            round_id=round_id,
            auction_type=self.auction_type,
            winner_id=winner_id,
            price_paid=price_paid,
            seller_revenue=seller_revenue,
            valuations=valuations,
            bids=bids,
            profits=profits,
        )
    
@dataclass
class SecondPriceAuction(Auction):
    """
    Second-price sealed-bid auction.
    """
    auction_type: str = "second_price"

    def run(
        self,
        round_id: int,
        valuations: dict[str, float],
        bids: dict[str, float],
    ) -> AuctionResult:
        if not bids:
            raise ValueError("Cannot run auction with no bids.")

        max_bid = max(bids.values())


        # Handle ties randomly among highest bidders.
        tied_winners = [
            agent_id for agent_id, bid in bids.items()
            if bid == max_bid
        ]
        winner_id = random.choice(tied_winners)
        if len(bids) == 1:
            price_paid = 0.0
        else:
            price_paid = heapq.nlargest(2, bids.values())[1]
        seller_revenue = price_paid
        
        profits = {}

        for agent_id, valuation in valuations.items():
            if agent_id == winner_id:
                profits[agent_id] = valuation - price_paid
            else:
                profits[agent_id] = 0.0
        
        return AuctionResult(
            round_id=round_id,
            auction_type=self.auction_type,
            winner_id=winner_id,
            price_paid=price_paid,
            seller_revenue=seller_revenue,
            valuations=valuations,
            bids=bids,
            profits=profits,
        )
