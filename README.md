# Auction and Market Strategy Simulator

## Overview

This project is a modular Python simulation framework for studying bidding
strategies, auction mechanisms, and double-auction markets. It supports
fixed-rule and adaptive agents, Monte Carlo experiments, economic metrics,
saved analytics, and an interactive Streamlit dashboard.

## Features

- First-price and second-price sealed-bid auctions
- Midpoint-price double-auction market clearing
- Truthful, random, shading, markup, and epsilon-greedy bandit agents
- Repeated auction and market simulations
- Competition and head-to-head strategy sweeps
- Profit, regret, revenue, surplus, volume, and efficiency metrics
- CSV and chart output
- Streamlit views for auctions, markets, and learning agents
- Automated tests for mechanisms, agents, metrics, experiments, and UI logic

## Architecture

```text
auction_sim/
  agents.py          Single-item auction agents
  auctions.py        First-price and second-price mechanisms
  bandits.py         Reusable epsilon-greedy policy
  simulation.py      Repeated auction simulation
  data.py            Auction result DataFrame conversion
  metrics.py         Auction and bidder analytics
  experiments.py     Baselines and parameter sweeps
  learning.py        Bandit comparisons and learning analytics

market_sim/
  market.py          Double-auction matching and result types
  market_agents.py   Buyer, seller, and adaptive buyer agents
  simulation.py      Repeated market simulation
  data.py            Market result DataFrame conversion
  metrics.py         Volume, surplus, and efficiency analytics
  experiments.py     Market scenarios and saved outputs
```

The auction and market engines are separate because their participants,
outcomes, and metrics differ. They share validation and adaptive-policy
components where the contracts genuinely overlap.

## Auction Mechanisms

### First Price

The highest bidder wins and pays their own bid. Bid shading can preserve
surplus but lowers the probability of winning.

### Second Price

The highest bidder wins and pays the second-highest bid. Truthful bidding is
the standard theoretical benchmark.

### Double Auction

Buyer bids are sorted from highest to lowest and seller asks from lowest to
highest. Orders trade while the bid crosses the ask. The transaction price is
the midpoint:

```text
price = (buyer_bid + seller_ask) / 2
```

## Agents

- `TruthfulAgent`: bids its private valuation.
- `RandomAgent`: samples a bid between zero and its valuation.
- `ShadingAgent`: bids a fixed valuation multiplier.
- `BanditAgent`: learns a bid multiplier with epsilon-greedy exploration.
- `TruthfulBuyerAgent`: submits its private value.
- `ShadingBuyerAgent`: submits a fixed fraction of its private value.
- `TruthfulSellerAgent`: asks its private cost.
- `MarkupSellerAgent`: asks its cost plus a fixed markup.
- `BanditBuyerAgent`: learns a buyer bid multiplier.

## Metrics

Auction analytics include profit, win rate, regret, seller revenue, winning
price, winner valuation, and allocative efficiency.

Market analytics include trade volume, transaction price, bid-ask spread,
buyer surplus, seller surplus, total surplus, unmatched participants, and
allocative efficiency. Market efficiency is realized surplus divided by the
maximum feasible surplus from private buyer values and seller costs.

## Run Locally

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest
python3 main.py
streamlit run streamlit_app.py
```

The dashboard defaults to 1,000 rounds and caps each participant side at 16
agents to keep hosted interactions responsive.

## Example Experiments

```python
from auction_sim.experiments import (
    run_competition_sweep,
    run_strategy_sweep,
)
from market_sim.experiments import run_market_scenarios

competition = run_competition_sweep(num_rounds=10_000)
strategies = run_strategy_sweep(num_rounds=10_000)
markets = run_market_scenarios(num_rounds=1_000)
```

These experiments are designed to investigate:

- how bidder competition changes seller revenue and bidder surplus
- which fixed shading multipliers perform best head-to-head
- how buyer/seller imbalance changes market volume and prices
- whether adaptive bandit agents learn profitable bidding multipliers

## Deployment

The app is configured for Streamlit Community Cloud. Deploy this repository
with `streamlit_app.py` as the entry point after connecting the GitHub
repository in Streamlit Community Cloud.

## Future Work

- Alternative clearing prices and continuous double auctions
- Reserve prices, budgets, and inventory constraints
- Additional valuation and cost distributions
- Seller-side adaptive agents
- Market regimes and correlated private information
