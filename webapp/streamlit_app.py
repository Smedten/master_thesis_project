import json
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Make project modules available when running `streamlit run webapp/streamlit_app.py`
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from evaluation.utils import plot_style  # noqa: E402


@st.cache_data
def load_evaluation_summary() -> pd.DataFrame:
    summary_path = ROOT / "evaluation" / "results" / "summary.csv"
    df = pd.read_csv(summary_path)
    df["MODE"] = df["MODE"].str.replace("_", " ")
    return df


@st.cache_data
def load_sample_scenarios() -> List[Dict]:
    scenario_path = ROOT / "evaluation" / "results" / "sample_scenarios.json"
    with scenario_path.open() as f:
        return json.load(f)


def build_schedule_chart(scenario: Dict) -> go.Figure:
    schedule_df = pd.DataFrame(scenario["schedule"])
    schedule_df["time"] = pd.to_datetime(schedule_df["time"])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=schedule_df["time"],
            y=schedule_df["max_power"],
            name="Max envelope",
            mode="lines",
            line=dict(color="#c7e9c0", dash="dot"),
            hovertemplate="%{y:.2f} kW",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=schedule_df["time"],
            y=schedule_df["min_power"],
            name="Min envelope",
            mode="lines",
            line=dict(color="#fdd0a2", dash="dot"),
            fill="tonexty",
            fillcolor="rgba(253,208,162,0.15)",
            hovertemplate="%{y:.2f} kW",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=schedule_df["time"],
            y=schedule_df["baseline_power"],
            name="Baseline schedule",
            mode="lines+markers",
            line=dict(color=plot_style.MARKET_COLORS.get("spot", "#1f77b4")),
            marker=dict(symbol="circle"),
            hovertemplate="%{y:.2f} kW",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=schedule_df["time"],
            y=schedule_df["optimized_power"],
            name="Optimized schedule",
            mode="lines+markers",
            line=dict(color=plot_style.MARKET_COLORS.get("reserve", "#ff7f0e")),
            marker=dict(symbol="diamond"),
            hovertemplate="%{y:.2f} kW",
        )
    )

    fig.update_layout(
        title="Aggregated flex-offer schedule",
        xaxis_title="Time",
        yaxis_title="Power (kW)",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=10, r=10, t=50, b=20),
        height=420,
    )
    return fig


def build_revenue_chart(scenario: Dict) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Baseline", "Optimized"],
            y=[scenario["baseline_revenue"], scenario["optimized_revenue"]],
            marker_color=[plot_style.MARKET_COLORS.get("spot"), plot_style.MARKET_COLORS.get("reserve")],
        )
    )
    fig.update_layout(
        title="Revenue comparison",
        yaxis_title="Revenue (DKK)",
        height=320,
    )
    return fig


def build_optimality_chart(summary_df: pd.DataFrame) -> go.Figure:
    grouped = (
        summary_df.groupby(["TYPE", "MODE", "CLUSTER_METHOD", "NUM_CLUSTERS"], as_index=False)["pct_of_optimal"]
        .mean()
        .sort_values(["TYPE", "MODE", "CLUSTER_METHOD", "NUM_CLUSTERS"])
    )

    fig = go.Figure()
    for (t, mode, method), subset in grouped.groupby(["TYPE", "MODE", "CLUSTER_METHOD"]):
        style = plot_style.MODE_STYLES.get(mode.replace(" ", "_"), "solid")
        marker = plot_style.MODE_MARKERS.get(mode.replace(" ", "_"), "circle")
        fig.add_trace(
            go.Scatter(
                x=subset["NUM_CLUSTERS"],
                y=subset["pct_of_optimal"],
                mode="lines+markers",
                name=f"{t} - {mode} - {method}",
                line=dict(dash=style),
                marker=dict(symbol=marker),
            )
        )

    fig.update_layout(
        title="Mean % of theoretical optimum by clustering",
        xaxis=dict(title="Clusters", type="category"),
        yaxis_title="% of optimal",
        height=420,
        legend=dict(orientation="h", y=-0.3),
    )
    return fig


def download_button(label: str, df: pd.DataFrame, file_name: str, description: str):
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
        help=description,
    )


def main():
    st.set_page_config(page_title="Flex-offer evaluation explorer", layout="wide")
    st.title("Flex-offer evaluation explorer")
    st.write(
        "Use this dashboard to explore aggregated flex-offer schedules, revenue uplift, and evaluation metrics."
    )

    summary_df = load_evaluation_summary()
    scenarios = load_sample_scenarios()
    scenario_lookup = {s["name"]: s for s in scenarios}

    with st.sidebar:
        st.header("Sample scenarios")
        selected_name = st.selectbox("Choose a scenario", list(scenario_lookup.keys()))
        scenario = scenario_lookup[selected_name]
        st.markdown(f"**Start:** {scenario['start']}  ")
        st.markdown(
            f"**Resolution:** {scenario['time_resolution_minutes']} minutes  "
        )
        st.caption(scenario["description"])

        st.markdown("---")
        st.header("Evaluation filters")
        st.caption("Interactively slice the evaluation summary with the bundled sample data.")

        type_options = sorted(summary_df["TYPE"].unique())
        mode_options = sorted(summary_df["MODE"].unique())
        cluster_options = sorted(summary_df["CLUSTER_METHOD"].unique())
        cluster_counts = sorted(summary_df["NUM_CLUSTERS"].unique())

        selected_types = st.multiselect("Type", type_options, default=type_options)
        selected_modes = st.multiselect("Mode", mode_options, default=mode_options)
        selected_clusters = st.multiselect(
            "Cluster method", cluster_options, default=cluster_options
        )
        selected_cluster_counts = st.multiselect(
            "Cluster count", cluster_counts, default=cluster_counts
        )

    filtered_summary = summary_df[
        summary_df["TYPE"].isin(selected_types)
        & summary_df["MODE"].isin(selected_modes)
        & summary_df["CLUSTER_METHOD"].isin(selected_clusters)
        & summary_df["NUM_CLUSTERS"].isin(selected_cluster_counts)
    ]

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("Aggregated flex-offer schedule")
        st.plotly_chart(build_schedule_chart(scenario), use_container_width=True)
    with col2:
        st.subheader("Revenue comparison")
        uplift = scenario["optimized_revenue"] - scenario["baseline_revenue"]
        st.metric("Optimized uplift (DKK)", f"{uplift:,.0f}")
        st.plotly_chart(build_revenue_chart(scenario), use_container_width=True)

    st.markdown("---")
    st.subheader("Evaluation summary")
    col3, col4 = st.columns([1, 1])

    if filtered_summary.empty:
        st.warning("No rows match the current filter selection. Adjust filters to see results.")
    else:
        with col3:
            st.plotly_chart(
                build_optimality_chart(filtered_summary), use_container_width=True
            )
        with col4:
            st.dataframe(filtered_summary, use_container_width=True, height=420)

    st.markdown("### Download results")
    schedule_df = pd.DataFrame(scenario["schedule"])  # type: ignore[arg-type]
    download_button(
        "Download selected schedule as CSV",
        schedule_df,
        f"{scenario['id']}_schedule.csv",
        "Aggregated flex-offer schedule with baseline and optimized allocations.",
    )
    download_button(
        "Download evaluation summary",
        summary_df,
        "evaluation_summary.csv",
        "Aggregated metrics from evaluation/results/summary.csv.",
    )

    st.markdown(
        """
        **How to use this page**

        * Pick a sample scenario to see its aggregated flex-offer schedule side-by-side for baseline and optimized plans.
        * Review the revenue uplift and download the exact schedule for further analysis or integration with other tools.
        * Use the evaluation summary to benchmark clustering strategies and market configurations across runs.
        """
    )


if __name__ == "__main__":
    main()
