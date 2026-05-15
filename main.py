from auction_sim.agents import RandomAgent, ShadingAgent, TruthfulAgent
from auction_sim.auctions import FirstPriceAuction, SecondPriceAuction
from auction_sim.data import results_to_dataframe
from auction_sim.metrics import summarize_agents, summarize_auction
from auction_sim.simulation import Simulation

def main():
    agents = [
        TruthfulAgent(agent_id="truthful_1"),
        RandomAgent(agent_id="random_1"),
        ShadingAgent(agent_id="shading_1", alpha =0.75)
    ]
    sim = Simulation(FirstPriceAuction(), num_rounds=10, agents=agents, seed=1453)
    results = sim.run()
    df = results_to_dataframe(results)

    auction_summary = summarize_auction(df)
    agent_summary = summarize_agents(df)

    print("\nAuction Summary")
    print("-" * 50)
    for key, value in auction_summary.items():
        print(f"{key}: {value}")

    print("\nAgent Summary")
    print("-" * 50)
    print(agent_summary.to_string(index=False))

    df.to_csv("outputs/results.csv", index=False)
    agent_summary.to_csv("outputs/agent_summary.csv", index=False)

if __name__ == "__main__":
    main()