from market_sim.market_agents import BuyerAgent, SellerAgent
from market_sim.simulation import MarketSimulation


class RecordingBuyer(BuyerAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.updates = []

    def bid(self, value, context=None):
        return value

    def update(self, result):
        self.updates.append(result)


class RecordingSeller(SellerAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.updates = []

    def ask(self, value, context=None):
        return value

    def update(self, result):
        self.updates.append(result)


def test_market_simulation_returns_repeated_complete_results():
    buyers = [RecordingBuyer("b1"), RecordingBuyer("b2")]
    sellers = [RecordingSeller("s1"), RecordingSeller("s2")]
    simulation = MarketSimulation(
        buyers=buyers,
        sellers=sellers,
        num_rounds=3,
        seed=7,
    )

    results = simulation.run()

    assert len(results) == 3
    assert all(set(result.buyer_bids) == {"b1", "b2"} for result in results)
    assert all(set(result.seller_asks) == {"s1", "s2"} for result in results)


def test_market_simulation_updates_all_agents_each_round():
    buyers = [RecordingBuyer("buyer")]
    sellers = [RecordingSeller("seller")]
    simulation = MarketSimulation(
        buyers=buyers,
        sellers=sellers,
        num_rounds=4,
        buyer_value_low=100,
        buyer_value_high=100,
        seller_cost_low=10,
        seller_cost_high=10,
    )

    simulation.run()

    assert len(buyers[0].updates) == 4
    assert len(sellers[0].updates) == 4
    assert all(update["traded"] for update in buyers[0].updates)
    assert all(update["traded"] for update in sellers[0].updates)


def test_market_simulation_reports_unmatched_agents():
    buyer = RecordingBuyer("buyer")
    seller = RecordingSeller("seller")
    simulation = MarketSimulation(
        buyers=[buyer],
        sellers=[seller],
        num_rounds=1,
        buyer_value_low=10,
        buyer_value_high=10,
        seller_cost_low=90,
        seller_cost_high=90,
    )

    simulation.run()

    assert buyer.updates[0]["traded"] is False
    assert buyer.updates[0]["profit"] == 0.0
    assert seller.updates[0]["traded"] is False
    assert seller.updates[0]["profit"] == 0.0
