from __future__ import annotations

import streamlit as st

from dashboard_logic import (
    run_auction_dashboard,
    run_learning_dashboard,
    run_market_dashboard,
)


st.set_page_config(
    page_title="Auction and Market Simulator",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def cached_auction_run(**kwargs):
    return run_auction_dashboard(**kwargs)


@st.cache_data(show_spinner=False)
def cached_market_run(**kwargs):
    return run_market_dashboard(**kwargs)


@st.cache_data(show_spinner=False)
def cached_learning_run(**kwargs):
    return run_learning_dashboard(**kwargs)


def metric_row(summary: dict, keys: list[tuple[str, str]]) -> None:
    columns = st.columns(len(keys))
    for column, (key, label) in zip(columns, keys):
        value = summary[key]
        display = f"{value:.3f}" if isinstance(value, float) else value
        column.metric(label, display)


def auction_view() -> None:
    with st.sidebar:
        st.subheader("Auction controls")
        auction_type = st.selectbox(
            "Auction type",
            ["first_price", "second_price"],
        )
        num_rounds = st.number_input(
            "Rounds",
            min_value=10,
            max_value=20_000,
            value=1_000,
            step=100,
        )
        bidder_count = st.slider("Bidders", 2, 16, 6)
        strategy = st.selectbox(
            "Strategy mix",
            ["mixed", "truthful", "shading", "bandit"],
        )
        alpha = st.slider("Shading multiplier", 0.1, 1.2, 0.8, 0.05)
        low_value, high_value = st.slider(
            "Valuation range",
            0.0,
            200.0,
            (0.0, 100.0),
            5.0,
        )
        seed = st.number_input("Seed", value=42, step=1)
        run = st.button("Run auction", type="primary")

    if run:
        try:
            with st.spinner("Running auction simulation..."):
                st.session_state["auction_result"] = cached_auction_run(
                    auction_type=auction_type,
                    num_rounds=int(num_rounds),
                    bidder_count=bidder_count,
                    strategy=strategy,
                    alpha=alpha,
                    low_value=low_value,
                    high_value=high_value,
                    seed=int(seed),
                )
        except ValueError as error:
            st.error(str(error))

    result = st.session_state.get("auction_result")
    if result:
        summary = result["auction_summary"]
        metric_row(
            summary,
            [
                ("avg_seller_revenue", "Avg revenue"),
                ("allocative_efficiency", "Efficiency"),
                ("avg_winning_price", "Avg price"),
                ("avg_winner_valuation", "Winner value"),
            ],
        )
        st.subheader("Agent leaderboard")
        st.dataframe(result["agent_summary"], use_container_width=True)
        chart_data = result["agent_summary"].set_index("agent_id")
        left, right = st.columns(2)
        left.bar_chart(chart_data["total_profit"])
        right.bar_chart(chart_data["win_rate"])


def market_view() -> None:
    with st.sidebar:
        st.subheader("Market controls")
        num_rounds = st.number_input(
            "Market rounds",
            min_value=10,
            max_value=20_000,
            value=1_000,
            step=100,
        )
        num_buyers = st.slider("Buyers", 1, 16, 8)
        num_sellers = st.slider("Sellers", 1, 16, 8)
        buyer_strategy = st.selectbox(
            "Buyer strategy",
            ["truthful", "shading", "bandit"],
        )
        seller_strategy = st.selectbox(
            "Seller strategy",
            ["truthful", "markup"],
        )
        buyer_alpha = st.slider("Buyer multiplier", 0.1, 1.2, 0.8, 0.05)
        seller_markup = st.slider("Seller markup", 0.0, 1.0, 0.2, 0.05)
        buyer_range = st.slider(
            "Buyer value range",
            0.0,
            200.0,
            (0.0, 100.0),
            5.0,
        )
        seller_range = st.slider(
            "Seller cost range",
            0.0,
            200.0,
            (0.0, 100.0),
            5.0,
        )
        seed = st.number_input("Market seed", value=42, step=1)
        run = st.button("Run market", type="primary")

    if run:
        try:
            with st.spinner("Running market simulation..."):
                st.session_state["market_result"] = cached_market_run(
                    num_rounds=int(num_rounds),
                    num_buyers=num_buyers,
                    num_sellers=num_sellers,
                    buyer_strategy=buyer_strategy,
                    seller_strategy=seller_strategy,
                    buyer_alpha=buyer_alpha,
                    seller_markup=seller_markup,
                    buyer_value_low=buyer_range[0],
                    buyer_value_high=buyer_range[1],
                    seller_cost_low=seller_range[0],
                    seller_cost_high=seller_range[1],
                    seed=int(seed),
                )
        except ValueError as error:
            st.error(str(error))

    result = st.session_state.get("market_result")
    if result:
        summary = result["market_summary"]
        metric_row(
            summary,
            [
                ("avg_trade_volume", "Avg volume"),
                ("avg_transaction_price", "Avg price"),
                ("avg_total_surplus", "Avg surplus"),
                ("allocative_efficiency", "Efficiency"),
            ],
        )
        st.subheader("Market leaderboard")
        st.dataframe(result["agent_summary"], use_container_width=True)
        round_data = result["results"].drop_duplicates("round_id")
        left, right = st.columns(2)
        left.line_chart(
            round_data.set_index("round_id")["trade_volume"],
        )
        right.line_chart(
            round_data.set_index("round_id")["avg_transaction_price"],
        )


def learning_view() -> None:
    with st.sidebar:
        st.subheader("Learning controls")
        num_rounds = st.number_input(
            "Learning rounds",
            min_value=50,
            max_value=20_000,
            value=1_000,
            step=100,
        )
        epsilon = st.slider("Exploration rate", 0.0, 1.0, 0.1, 0.05)
        seed = st.number_input("Learning seed", value=42, step=1)
        run = st.button("Run learning comparison", type="primary")

    if run:
        with st.spinner("Training bandit agent..."):
            st.session_state["learning_result"] = cached_learning_run(
                num_rounds=int(num_rounds),
                epsilon=epsilon,
                seed=int(seed),
            )

    result = st.session_state.get("learning_result")
    if result:
        st.subheader("Fixed vs adaptive agents")
        st.dataframe(result["agent_summary"], use_container_width=True)
        cumulative = result["cumulative_profit"].pivot(
            index="round_id",
            columns="agent_id",
            values="cumulative_profit",
        )
        st.line_chart(cumulative)
        left, right = st.columns(2)
        left.subheader("Action frequency")
        left.bar_chart(
            result["action_summary"].set_index("action")["count"],
        )
        right.subheader("Estimated reward")
        right.bar_chart(
            result["action_summary"].set_index("action")["avg_reward"],
        )


st.title("Auction and Market Simulator")
view = st.segmented_control(
    "View",
    ["Auction Simulator", "Market Simulator", "Learning Agents"],
    default="Auction Simulator",
)

if view == "Auction Simulator":
    auction_view()
elif view == "Market Simulator":
    market_view()
else:
    learning_view()
