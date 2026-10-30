"""Phase 5: bar chart of average temperature per device."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

DEFAULT_INPUT = "output/summary.json"
DEFAULT_OUTPUT = "output/avg_temperature.png"


class ChartError(Exception):
    """The chart can't be produced (bad input file, missing matplotlib, etc.)."""


def load_summary(path: str | Path) -> list[dict[str, Any]]:
    """Read the JSON written by the CLI and return [{device_id, avg_temperature}, ...]."""
    path = Path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ChartError(f"File not found: {path}") from None
    except (OSError, ValueError) as exc:  # ValueError covers bad JSON and bad encoding
        raise ChartError(f"Could not read {path}: {exc}") from exc

    try:
        return [
            {"device_id": str(d["device_id"]), "avg_temperature": float(d["avg_temperature"])}
            for d in payload["devices"]
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise ChartError(f"{path} is not a valid summary file: {exc!r}") from exc


def _pyplot():
    try:
        import matplotlib

        matplotlib.use("Agg")  # headless: we only save to a file
        import matplotlib.pyplot as plt
    except ImportError:
        raise ChartError("matplotlib is required for charts: pip install matplotlib") from None
    return plt


def build_figure(devices: Sequence[dict[str, Any]]):
    """Create the bar chart figure (does not save or close it)."""
    if not devices:
        raise ChartError("No devices to plot.")

    plt = _pyplot()
    names = [d["device_id"] for d in devices]
    temps = [d["avg_temperature"] for d in devices]

    fig, ax = plt.subplots(figsize=(max(6.0, 1.0 * len(names)), 5.5))
    bars = ax.bar(names, temps, color="#4C78A8")
    ax.bar_label(bars, fmt="%.2f", padding=3)

    ax.set_title("Average Temperature per Device")
    ax.set_xlabel("Device")
    ax.set_ylabel("Average temperature")
    ax.set_ylim(0, max(temps) * 1.15 if max(temps) > 0 else 1)
    ax.tick_params(axis="x", labelrotation=45)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    fig.tight_layout()
    return fig


def plot_avg_temperature(devices: Sequence[dict[str, Any]], output_path: str | Path) -> Path:
    """Build the chart and save it as an image. Returns the output path."""
    output_path = Path(output_path)
    fig = build_figure(devices)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)
    except OSError as exc:
        raise ChartError(f"Could not write {output_path}: {exc}") from exc
    finally:
        _pyplot().close(fig)
    return output_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="devlog.charts",
        description="Plot average temperature per device from the summary JSON.",
    )
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT, help="summary JSON path")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help="chart image path")
    args = parser.parse_args(argv)

    try:
        plot_avg_temperature(load_summary(args.input), args.output)
    except ChartError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved chart to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
