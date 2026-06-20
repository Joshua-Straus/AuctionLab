from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Trade:
    buyer_id: str
    seller_id: str
    buyer_value: float
    seller_cost: float
    buyer_bid: float
    seller_ask: float
    price: float
    buyer_profit: float
    seller_profit: float


@dataclass(frozen=True)
class MarketResult:
    round_id: int
    trades: list[Trade]
    buyer_values: dict[str, float]
    seller_costs: dict[str, float]
    buyer_bids: dict[str, float]
    seller_asks: dict[str, float]


@dataclass
class DoubleAuction:
    """Matches price-priority orders using midpoint transaction prices."""

    def run(
        self,
        round_id: int,
        buyer_valuations: dict[str, float],
        seller_valuations: dict[str, float],
        buyer_bids: dict[str, float] | None = None,
        seller_asks: dict[str, float] | None = None,
    ) -> MarketResult:
        if buyer_bids is None or seller_asks is None:
            raise ValueError("Buyer bids and seller asks are required.")
        if set(buyer_bids) != set(buyer_valuations):
            raise ValueError("Buyer bids and valuations must use the same agent IDs.")
        if set(seller_asks) != set(seller_valuations):
            raise ValueError("Seller asks and valuations must use the same agent IDs.")
        if any(value < 0 for value in buyer_valuations.values()):
            raise ValueError("Buyer valuations cannot be negative.")
        if any(cost < 0 for cost in seller_valuations.values()):
            raise ValueError("Seller costs cannot be negative.")
        if any(bid < 0 for bid in buyer_bids.values()):
            raise ValueError("Buyer bids cannot be negative.")
        if any(ask < 0 for ask in seller_asks.values()):
            raise ValueError("Seller asks cannot be negative.")

        sorted_buyers = sorted(
            buyer_bids.items(),
            key=lambda item: (-item[1], item[0]),
        )
        sorted_sellers = sorted(
            seller_asks.items(),
            key=lambda item: (item[1], item[0]),
        )

        trades: list[Trade] = []
        for (buyer_id, buyer_bid), (seller_id, seller_ask) in zip(
            sorted_buyers,
            sorted_sellers,
        ):
            if buyer_bid < seller_ask:
                break

            price = (buyer_bid + seller_ask) / 2
            buyer_value = buyer_valuations[buyer_id]
            seller_cost = seller_valuations[seller_id]
            trades.append(
                Trade(
                    buyer_id=buyer_id,
                    seller_id=seller_id,
                    buyer_value=buyer_value,
                    seller_cost=seller_cost,
                    buyer_bid=buyer_bid,
                    seller_ask=seller_ask,
                    price=price,
                    buyer_profit=buyer_value - price,
                    seller_profit=price - seller_cost,
                )
            )

        return MarketResult(
            round_id=round_id,
            trades=trades,
            buyer_values=dict(buyer_valuations),
            seller_costs=dict(seller_valuations),
            buyer_bids=dict(buyer_bids),
            seller_asks=dict(seller_asks),
        )
