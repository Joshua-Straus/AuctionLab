"""
File to define different auction mechanisms.
"""

from __future__ import annotations

import heapq
import random
from dataclasses import dataclass

from auction_sim.results import AuctionResult


def _select_winner(bids: dict[str, float]) -> str:
    """Choose uniformly among bidders tied for the highest bid."""
    if not bids:
        raise ValueError("Cannot run auction with no bids.")

    highest_bid = max(bids.values())
    tied_winners = [
        agent_id for agent_id, bid in bids.items() if bid == highest_bid
    ]
    return random.choice(tied_winners)


def _calculate_profits(
    valuations: dict[str, float], winner_id: str, price_paid: float
) -> dict[str, float]:
    return {
        agent_id: valuation - price_paid if agent_id == winner_id else 0.0
        for agent_id, valuation in valuations.items()
    }


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
        winner_id = _select_winner(bids)
        price_paid = bids[winner_id]

        return AuctionResult(
            round_id=round_id,
            auction_type=self.auction_type,
            winner_id=winner_id,
            price_paid=price_paid,
            seller_revenue=price_paid,
            valuations=valuations,
            bids=bids,
            profits=_calculate_profits(valuations, winner_id, price_paid),
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
        winner_id = _select_winner(bids)
        price_paid = (
            heapq.nlargest(2, bids.values())[1] if len(bids) > 1 else 0.0
        )

        return AuctionResult(
            round_id=round_id,
            auction_type=self.auction_type,
            winner_id=winner_id,
            price_paid=price_paid,
            seller_revenue=price_paid,
            valuations=valuations,
            bids=bids,
            profits=_calculate_profits(valuations, winner_id, price_paid),
        )
