"""
File to define different auction mechanisms.
"""

from __future__ import annotations

import heapq
import math
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


@dataclass
class EnglishAuction(Auction):
    """Ascending auction with 100 equal increments across its bid range."""

    auction_type: str = "english"
    min_bid: float = 0.0
    max_bid: float = 100.0

    def __post_init__(self) -> None:
        if self.min_bid >= self.max_bid:
            raise ValueError("max_bid must be greater than min_bid.")

    @property
    def bid_increment(self) -> float:
        return (self.max_bid - self.min_bid) / 100

    def run(
        self,
        round_id: int,
        valuations: dict[str, float],
        bids: dict[str, float],
    ) -> AuctionResult:
        if not bids:
            raise ValueError("Cannot run auction with no bids.")

        bounded_bids = {
            agent_id: min(self.max_bid, max(self.min_bid, bid))
            for agent_id, bid in bids.items()
        }
        highest_bid = max(bounded_bids.values())
        tied_winners = [
            agent_id
            for agent_id, bid in bounded_bids.items()
            if bid == highest_bid
        ]
        winner_id = random.choice(tied_winners)
        price_paid = (
            heapq.nlargest(2, bounded_bids.values())[1]
            if len(bounded_bids) > 1
            else self.min_bid
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


@dataclass
class DutchAuction(Auction):
    """Descending auction with 100 equal decrements across its bid range."""

    auction_type: str = "dutch"
    min_bid: float = 0.0
    max_bid: float = 100.0

    def __post_init__(self) -> None:
        if self.min_bid >= self.max_bid:
            raise ValueError("max_bid must be greater than min_bid.")

    @property
    def bid_decrement(self) -> float:
        return (self.max_bid - self.min_bid) / 100

    def _acceptance_step(self, bid: float) -> int:
        """Return the first descending-clock step a maximum bid accepts."""
        bounded_bid = min(self.max_bid, max(self.min_bid, bid))
        return min(
            100,
            math.ceil(
                (self.max_bid - bounded_bid) / self.bid_decrement - 1e-12
            ),
        )

    def run(
        self,
        round_id: int,
        valuations: dict[str, float],
        bids: dict[str, float],
    ) -> AuctionResult:
        if not bids:
            raise ValueError("Cannot run auction with no bids.")

        acceptance_steps = {
            agent_id: self._acceptance_step(bid)
            for agent_id, bid in bids.items()
        }
        winning_step = min(acceptance_steps.values())
        tied_winners = [
            agent_id
            for agent_id, step in acceptance_steps.items()
            if step == winning_step
        ]
        winner_id = random.choice(tied_winners)
        price_paid = self.max_bid - winning_step * self.bid_decrement

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
class TheoreticalEnglishAuction(Auction):
    """Continuous English auction settling at the second-highest value."""

    auction_type: str = "theoretical_english"

    def run(
        self,
        round_id: int,
        valuations: dict[str, float],
        bids: dict[str, float],
    ) -> AuctionResult:
        if len(valuations) < 2:
            raise ValueError("Theoretical English auctions require at least two bidders.")

        winner_id = _select_winner(valuations)
        price_paid = heapq.nlargest(2, valuations.values())[1]
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
class TheoreticalDutchAuction(Auction):
    """Continuous Dutch auction settling at the highest stopping price."""

    auction_type: str = "theoretical_dutch"

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
