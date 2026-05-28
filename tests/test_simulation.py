from auction_sim.agents import ShadingAgent, TruthfulAgent
from auction_sim.auctions import FirstPriceAuction
from auction_sim.simulation import Simulation


def test_simulation_returns_full_round_result_with_all_agent_bids():
    agents = [
        TruthfulAgent(agent_id="truthful"),
        ShadingAgent(agent_id="shade", alpha=0.7),
    ]

    sim = Simulation(
        auction=FirstPriceAuction(),
        agents=agents,
        num_rounds=1,
        low_value=100,
        high_value=100,
        seed=42,
    )

    results = sim.run()

    assert len(results) == 1
    assert set(results[0].bids) == {"truthful", "shade"}
    assert set(results[0].valuations) == {"truthful", "shade"}
    assert set(results[0].profits) == {"truthful", "shade"}
