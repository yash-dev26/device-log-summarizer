"""Phase 4: format device summaries as a plain-text table."""

from __future__ import annotations

from collections.abc import Sequence

from devlog.models import DeviceSummary

HEADERS = ("Device", "Records", "Avg Temp", "Errors")


def format_table(summaries: Sequence[DeviceSummary]) -> str:
    """Return a fixed-width table (device left-aligned, numbers right-aligned)."""
    if not summaries:
        return "No devices to display."

    rows = [
        (s.device_id, str(s.total_records), f"{s.avg_temperature:.2f}", str(s.error_count))
        for s in summaries
    ]
    widths = [max(len(cell) for cell in column) for column in zip(HEADERS, *rows)]

    def render(cells: Sequence[str]) -> str:
        parts = [
            cell.ljust(width) if index == 0 else cell.rjust(width)
            for index, (cell, width) in enumerate(zip(cells, widths))
        ]
        return "  ".join(parts)

    separator = "  ".join("-" * width for width in widths)
    return "\n".join([render(HEADERS), separator, *(render(row) for row in rows)])
