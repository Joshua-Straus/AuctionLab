from __future__ import annotations

import streamlit as st

from frontend.api_client import ApiError, SimulatorApiClient


st.set_page_config(
    page_title="Auction Strategy Research",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def cached_auction_run(**kwargs):
    return SimulatorApiClient().run_auction(kwargs)


@st.cache_data(show_spinner=False)
def cached_learning_run(**kwargs):
    return SimulatorApiClient().run_learning(kwargs)


@st.cache_data(show_spinner=False)
def cached_vickrey_run(**kwargs):
    return SimulatorApiClient().run_vickrey(kwargs)


@st.cache_data(show_spinner=False)
def cached_first_price_strategy_run(**kwargs):
    return SimulatorApiClient().run_first_price_strategies(kwargs)


@st.cache_data(show_spinner=False)
def cached_revenue_equality_run(**kwargs):
    return SimulatorApiClient().run_revenue_equality(kwargs)


@st.cache_data(ttl=30, show_spinner=False)
def cached_experiments():
    return SimulatorApiClient().list_experiments()


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
        except ApiError as error:
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


def vickrey_view() -> None:
    st.subheader("Vickrey (Second Price) Auction Test")
    st.markdown(
        "Tests the proposition: **“Bidding your valuation is a weakly-dominant "
        "strategy in a second-price auction.”** Truthful, fixed-shading, and "
        "adaptive bandit bidders compete in the same repeated auctions."
    )
    with st.sidebar:
        st.subheader("Vickrey test controls")
        num_rounds = st.number_input(
            "Vickrey rounds",
            min_value=100,
            max_value=20_000,
            value=5_000,
            step=500,
        )
        agents_per_strategy = st.slider("Agents per strategy", 1, 5, 3)
        shading_alpha = st.slider(
            "Vickrey shading multiplier", 0.1, 1.0, 0.8, 0.05
        )
        epsilon = st.slider(
            "Vickrey bandit exploration", 0.0, 1.0, 0.1, 0.05
        )
        value_range = st.slider(
            "Vickrey valuation range",
            0.0,
            200.0,
            (0.0, 100.0),
            5.0,
        )
        seed = st.number_input("Vickrey seed", value=42, step=1)
        run = st.button("Run Vickrey test", type="primary")

    if run:
        try:
            with st.spinner("Testing truthful bidding in a Vickrey auction..."):
                st.session_state["vickrey_result"] = cached_vickrey_run(
                    num_rounds=int(num_rounds),
                    agents_per_strategy=agents_per_strategy,
                    shading_alpha=shading_alpha,
                    epsilon=epsilon,
                    low_value=value_range[0],
                    high_value=value_range[1],
                    seed=int(seed),
                )
        except ApiError as error:
            st.error(str(error))

    result = st.session_state.get("vickrey_result")
    if not result:
        st.info("Run the experiment to compare expected profit by bidding strategy.")
        return

    proposition = result["proposition"]
    metric_row(
        proposition,
        [
            ("truthful_expected_profit", "Truthful expected profit"),
            ("shading_expected_profit", "Shading expected profit"),
            ("bandit_expected_profit", "Bandit expected profit"),
        ],
    )
    if proposition["supports_proposition"]:
        st.success(proposition["interpretation"])
    else:
        st.warning(proposition["interpretation"])
    st.caption(
        "Expected profit is mean profit per bidder per auction. This Monte Carlo "
        "result illustrates the theoretical proposition but does not replace its proof."
    )

    strategy_summary = result["strategy_summary"]
    left, right = st.columns(2)
    left.subheader("Expected profit by strategy")
    left.bar_chart(strategy_summary.set_index("strategy")["expected_profit"])
    right.subheader("Average bid/value ratio")
    right.bar_chart(strategy_summary.set_index("strategy")["avg_bid_to_value"])
    st.subheader("Strategy comparison")
    st.dataframe(strategy_summary, use_container_width=True, hide_index=True)
    with st.expander("Agent-level results"):
        st.dataframe(result["agent_summary"], use_container_width=True, hide_index=True)


def first_price_strategy_view() -> None:
    st.subheader("Sealed Bid (First-Price) Auction")
    st.markdown(
        "Answers the question: **Which agent type makes the most profit on "
        "average?** Equal cohorts of truthful, random, fixed-shading, adaptive "
        "bandit, and equilibrium bidders compete in repeated first-price auctions."
    )
    with st.sidebar:
        st.subheader("First-price test controls")
        num_rounds = st.number_input(
            "First-price test rounds",
            min_value=100,
            max_value=20_000,
            value=5_000,
            step=500,
        )
        agents_per_strategy = st.slider(
            "First-price agents per strategy", 1, 3, 3
        )
        shading_alpha = st.slider(
            "First-price shading multiplier", 0.1, 1.0, 0.8, 0.05
        )
        epsilon = st.slider(
            "First-price bandit exploration", 0.0, 1.0, 0.1, 0.05
        )
        value_range = st.slider(
            "First-price valuation range",
            0.0,
            200.0,
            (0.0, 100.0),
            5.0,
        )
        seed = st.number_input("First-price test seed", value=42, step=1)
        run = st.button("Run first-price test", type="primary")

    if run:
        try:
            with st.spinner("Comparing all first-price bidding strategies..."):
                st.session_state[
                    "first_price_result"
                ] = cached_first_price_strategy_run(
                    num_rounds=int(num_rounds),
                    agents_per_strategy=agents_per_strategy,
                    shading_alpha=shading_alpha,
                    epsilon=epsilon,
                    low_value=value_range[0],
                    high_value=value_range[1],
                    seed=int(seed),
                )
        except ApiError as error:
            st.error(str(error))

    result = st.session_state.get("first_price_result")
    if not result:
        st.info("Run the experiment to compare average profit by agent type.")
        return

    comparison = result["comparison"]
    st.success(comparison["interpretation"])
    metric_row(
        comparison,
        [
            ("highest_expected_profit", "Highest expected profit"),
            ("equilibrium_bid_multiplier", "Equilibrium bid multiplier"),
            ("total_agents", "Total bidders"),
        ],
    )
    st.caption(
        "Expected profit is mean profit per bidder per auction. The equilibrium "
        "agent bids b(v) = [(n−1)/n]v using the displayed total bidder count."
    )

    strategy_summary = result["strategy_summary"]
    left, right = st.columns(2)
    left.subheader("Expected profit by agent type")
    left.bar_chart(strategy_summary.set_index("strategy")["expected_profit"])
    right.subheader("Average bid/value ratio")
    right.bar_chart(strategy_summary.set_index("strategy")["avg_bid_to_value"])
    st.subheader("Strategy comparison")
    st.dataframe(strategy_summary, use_container_width=True, hide_index=True)
    with st.expander("Agent-level results"):
        st.dataframe(result["agent_summary"], use_container_width=True, hide_index=True)


def revenue_equality_view() -> None:
    st.subheader("Revenue Equality")
    st.markdown(
        "Tests whether a first-price auction with equilibrium bidders and a "
        "second-price auction with truthful bidders produce the same expected "
        "seller revenue under identical I.I.D. private values."
    )
    with st.sidebar:
        st.subheader("Revenue equality controls")
        num_rounds = st.number_input(
            "Revenue equality trials",
            min_value=100,
            max_value=20_000,
            value=10_000,
            step=1_000,
        )
        bidder_count = st.slider("I.I.D. bidders per auction", 2, 64, 16)
        value_range = st.slider(
            "Revenue equality valuation range",
            0.0,
            200.0,
            (0.0, 100.0),
            5.0,
        )
        seed = st.number_input("Revenue equality seed", value=42, step=1)
        run = st.button("Run revenue equality test", type="primary")

    if run:
        try:
            with st.spinner("Running paired first- and second-price trials..."):
                st.session_state[
                    "revenue_equality_result"
                ] = cached_revenue_equality_run(
                    num_rounds=int(num_rounds),
                    bidder_count=bidder_count,
                    low_value=value_range[0],
                    high_value=value_range[1],
                    seed=int(seed),
                )
        except ApiError as error:
            st.error(str(error))

    result = st.session_state.get("revenue_equality_result")
    if not result:
        st.info("Run the experiment to compare seller revenue by auction format.")
        return

    comparison = result["comparison"]
    metric_row(
        comparison,
        [
            ("first_price_average_revenue", "First-price avg revenue"),
            ("second_price_average_revenue", "Second-price avg revenue"),
            ("average_revenue_difference", "Average difference"),
        ],
    )
    if comparison["consistent_with_revenue_equality"]:
        st.success(comparison["interpretation"])
    else:
        st.warning(comparison["interpretation"])
    st.caption(
        "Difference is first-price minus second-price revenue. The test uses a "
        "paired 95% confidence interval and records seller revenue for every trial."
    )

    format_summary = result["format_summary"]
    revenue_by_trial = result["revenue_by_trial"]
    left, right = st.columns(2)
    left.subheader("Average seller revenue")
    left.bar_chart(
        format_summary.set_index("auction_format")["average_seller_revenue"]
    )
    right.subheader("Running average revenue")
    revenue_pivot = revenue_by_trial.pivot(
        index="round_id",
        columns="auction_format",
        values="seller_revenue",
    )
    right.line_chart(revenue_pivot.expanding().mean())
    st.subheader("Auction-format summary")
    st.dataframe(format_summary, use_container_width=True, hide_index=True)
    with st.expander("Trial-level seller revenue"):
        st.dataframe(revenue_by_trial, use_container_width=True, hide_index=True)


st.title("Auction Strategy Research")

try:
    experiments = cached_experiments()
except ApiError as error:
    experiments = []
    st.warning(f"FastAPI is unavailable. Start the backend to run simulations. ({error})")

if experiments:
    with st.expander("Pre-made experiments"):
        labels = {experiment["name"]: experiment for experiment in experiments}
        selected_name = st.selectbox("Experiment", list(labels))
        selected = labels[selected_name]
        st.caption(selected["description"])
        if st.button("Run pre-made experiment"):
            try:
                with st.spinner("Running stored experiment..."):
                    result = SimulatorApiClient().run_experiment(
                        selected["slug"]
                    )
                st.session_state[f"{selected['kind']}_result"] = result
                st.success("Experiment complete. Open its matching view below.")
            except ApiError as error:
                st.error(str(error))

view = st.segmented_control(
    "View",
    [
        "Auction Simulator",
        "Sealed Bid (First-Price) Auction",
        "Vickrey (Second Price) Auction Test",
        "Revenue Equality",
        "Learning Agents",
    ],
    default="Auction Simulator",
)

if view == "Auction Simulator":
    auction_view()
elif view == "Sealed Bid (First-Price) Auction":
    first_price_strategy_view()
elif view == "Vickrey (Second Price) Auction Test":
    vickrey_view()
elif view == "Revenue Equality":
    revenue_equality_view()
else:
    learning_view()
