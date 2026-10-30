"""Phase 4: command-line interface tying the pipeline together."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from devlog.aggregate import MAX_AVG_TEMPERATURE, filter_by_avg_temperature, summarize_devices
from devlog.export import write_json
from devlog.ingest import TelemetryFileError, load_records
from devlog.report import format_table

DEFAULT_OUTPUT = "output/summary.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devlog",
        description="Summarize device telemetry from a CSV file.",
    )
    parser.add_argument("input", help="path to the telemetry CSV file")
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT, help=f"JSON output path (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--max-avg",
        type=float,
        default=MAX_AVG_TEMPERATURE,
        help=f"drop devices with an average temperature above this (default: {MAX_AVG_TEMPERATURE})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code (0 = success, 1 = error)."""
    args = build_parser().parse_args(argv)

    try:
        result = load_records(args.input)
    except TelemetryFileError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for skipped in result.skipped:
        print(f"warning: skipped line {skipped.line_number}: {skipped.reason}", file=sys.stderr)

    summaries = summarize_devices(result.records)
    kept = filter_by_avg_temperature(summaries, args.max_avg)
    kept_ids = {s.device_id for s in kept}
    dropped_ids = [s.device_id for s in summaries if s.device_id not in kept_ids]

    print(format_table(kept))
    if dropped_ids:
        print(
            f"\nFiltered out {len(dropped_ids)} device(s) with avg temperature "
            f"above {args.max_avg}: {', '.join(dropped_ids)}"
        )

    try:
        write_json(kept, args.output)
    except OSError as exc:
        print(f"error: could not write {args.output}: {exc}", file=sys.stderr)
        return 1

    print(f"\nSaved results to {args.output}")
    return 0
