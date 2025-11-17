"""Lightweight matplotlib dashboard for evaluation results.

Run ``python -m evaluation.dashboard`` after the simulations have written
``evaluation/results/summary.csv`` to generate a 2×2 overview figure that
summarizes savings, market contributions, runtimes, and optimality for
all scenarios in the CSV.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt
import pandas as pd

DEFAULT_RESULTS = Path("evaluation/results/summary.csv")
DEFAULT_OUTPUT = Path("evaluation/results/dashboard_overview.png")


REQUIRED_COLUMNS = [
    "TYPE",
    "MODE",
    "RUN_SPOT",
    "RUN_RESERVE",
    "RUN_ACTIVATION",
    "NUM_EVS",
    "TIME_RES",
    "pct_total_saved",
    "pct_saved_spot",
    "pct_gain_res",
    "pct_gain_act",
    "runtime_scheduling",
    "runtime_aggregation",
    "pct_of_optimal",
]

OPTIONAL_COLUMNS = ["runtime_clustering"]


def _scenario_labels(df: pd.DataFrame) -> List[str]:
    labels: List[str] = []
    for _, row in df.iterrows():
        pieces: Iterable[str] = (
            f"{row['TYPE']}",
            f"{row['MODE']}",
            f"{int(row['NUM_EVS'])}ev",
            f"{int(row['TIME_RES'])}s",
            "R" if row["RUN_RESERVE"] else "",
            "A" if row["RUN_ACTIVATION"] else "",
        )
        label = " | ".join([p for p in pieces if p])
        labels.append(label)
    return labels


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns in results file: {', '.join(missing)}."
        )


def _runtime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with the runtime columns that are present."""
    runtime_df = pd.DataFrame()
    runtime_df["runtime_scheduling"] = df["runtime_scheduling"]
    runtime_df["runtime_aggregation"] = df["runtime_aggregation"]
    if "runtime_clustering" in df.columns:
        runtime_df["runtime_clustering"] = df["runtime_clustering"]
    else:
        runtime_df["runtime_clustering"] = 0.0
    return runtime_df


def build_dashboard(df: pd.DataFrame) -> plt.Figure:
    """Create an overview figure summarizing the evaluation results."""
    _validate_columns(df)

    labels = _scenario_labels(df)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("FlexOffer Evaluation Overview", fontsize=14, weight="bold")

    positions = list(range(len(labels)))

    # Savings vs greedy baseline
    axes[0, 0].bar(positions, df["pct_total_saved"], color="steelblue")
    axes[0, 0].set_title("Savings vs baseline (%)")
    axes[0, 0].set_xticks(positions)
    axes[0, 0].set_xticklabels(labels, rotation=30, ha="right")
    axes[0, 0].set_ylabel("% vs greedy baseline")

    # Market contributions (stacked bars)
    axes[0, 1].bar(positions, df["pct_saved_spot"], label="Spot", color="#4c78a8")
    axes[0, 1].bar(
        positions,
        df["pct_gain_res"],
        bottom=df["pct_saved_spot"],
        label="Reserve",
        color="#f58518",
    )
    bottom = df["pct_saved_spot"] + df["pct_gain_res"]
    axes[0, 1].bar(
        positions,
        df["pct_gain_act"],
        bottom=bottom,
        label="Activation",
        color="#54a24b",
    )
    axes[0, 1].set_title("Market contributions (%)")
    axes[0, 1].set_xticks(positions)
    axes[0, 1].set_xticklabels(labels, rotation=30, ha="right")
    axes[0, 1].legend()

    # Runtime breakdown (stacked bars)
    runtime_df = _runtime_columns(df)

    axes[1, 0].bar(
        positions,
        runtime_df["runtime_scheduling"],
        label="Scheduling",
        color="#72b7b2",
    )
    axes[1, 0].bar(
        positions,
        runtime_df["runtime_aggregation"],
        bottom=runtime_df["runtime_scheduling"],
        label="Aggregation",
        color="#e45756",
    )
    bottom_runtime = runtime_df["runtime_scheduling"] + runtime_df["runtime_aggregation"]
    axes[1, 0].bar(
        positions,
        runtime_df["runtime_clustering"],
        bottom=bottom_runtime,
        label="Clustering",
        color="#a0cbe8",
    )
    axes[1, 0].set_title("Runtime by stage (seconds)")
    axes[1, 0].set_xticks(positions)
    axes[1, 0].set_xticklabels(labels, rotation=30, ha="right")
    axes[1, 0].legend()

    # Percent of theoretical optimum
    axes[1, 1].bar(positions, df["pct_of_optimal"], color="#9d755d")
    axes[1, 1].set_ylim(0, 105)
    axes[1, 1].set_title("Percent of theoretical optimum (%)")
    axes[1, 1].set_xticks(positions)
    axes[1, 1].set_xticklabels(labels, rotation=30, ha="right")
    axes[1, 1].set_ylabel("% of optimum")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


def main():
    parser = argparse.ArgumentParser(
        description="Launch a matplotlib dashboard for evaluation results."
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=DEFAULT_RESULTS,
        help="Path to evaluation summary CSV (default: evaluation/results/summary.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=(
            "Path to save the dashboard PNG. Set to '' to disable saving. "
            "Default: evaluation/results/dashboard_overview.png"
        ),
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Open the figure in an interactive window in addition to saving it.",
    )

    args = parser.parse_args()

    df = pd.read_csv(args.results)
    fig = build_dashboard(df)

    if args.output:
        output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=200)
        print(f"Dashboard written to {output_path}")

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
