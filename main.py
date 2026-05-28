from auction_sim.display import print_experiment_summary
from auction_sim.experiments import run_baseline_comparison


def main():
    results = run_baseline_comparison(num_rounds=10_000)

    for auction_name, experiment_result in results.items():
        print_experiment_summary(
            auction_name=auction_name,
            auction_summary=experiment_result["auction_summary"],
            agent_summary=experiment_result["agent_summary"],
        )


if __name__ == "__main__":
    main()
