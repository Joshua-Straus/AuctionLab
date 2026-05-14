from auction_sim.results import AuctionResult


def print_auction_result(result: AuctionResult) -> None:
    print(f"Round {result.round_id}")
    print(f"Auction type: {result.auction_type}")
    print(f"Winner: {result.winner_id}")
    print(f"Price paid: {result.price_paid:.2f}")
    print(f"Seller revenue: {result.seller_revenue:.2f}")

    print("Bids:")
    for agent_id, bid in result.bids.items():
        value = result.valuations[agent_id]
        profit = result.profits[agent_id]
        print(
            f"  {agent_id}: "
            f"value={value:.2f}, "
            f"bid={bid:.2f}, "
            f"profit={profit:.2f}"
        )

    print("-" * 50)