from dataclasses import dataclass


@dataclass
class BidRecord:
    round_id: int
    agent_id: str
    valuation: float
    bid: float

@dataclass
class AuctionResult:
    round_id: int
    auction_type: str
    winner_id: str
    price_paid: float
    seller_revenue: float
    valuations: dict[str, float]
    bids: dict[str, float]
    profits: dict[str, float]