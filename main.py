from auction_sim.experiments import run_baseline_comparison

def main():
    results = run_baseline_comparison(num_rounds=10_000)

    for auction_name, experiment_result in results.items():
        print("\n" + "=" * 70)
        print(f"Auction: {auction_name}")
        print("=" * 70)

        print("\nAuction Summary")
        print("-" * 70)
        for key, value in experiment_result["auction_summary"].items():
            print(f"{key}: {value}")

        print("\nAgent Summary")
        print("-" * 70)
        print(experiment_result["agent_summary"].to_string(index=False))


if __name__ == "__main__":
    main()