from auction_sim.agents import RandomAgent, ShadingAgent, TruthfulAgent
from auction_sim.display import print_auction_result
from auction_sim.simulation import Simulation
from auction_sim.auctions import FirstPriceAuction

def main():
    agents = [
        TruthfulAgent(agent_id="truthful_1"),
        RandomAgent(agent_id="random_1"),
        ShadingAgent(agent_id="shading_1", alpha =0.75)
    ]
    sim = Simulation(FirstPriceAuction(), num_rounds=10, agents=agents, seed=1453)
    results = sim.run()
    print("Running first-price auction simulation...\n")

    for result in results:
        print_auction_result(result)

if __name__ == "__main__":
    main()