"""Phase 2: read device telemetry from CSV into typed records."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path

from devlog.models import Status, TelemetryRecord

REQUIRED_COLUMNS = ("device_id", "status", "temperature")


class TelemetryFileError(Exception):
    """The CSV file as a whole can't be used (missing, unreadable, wrong columns)."""


@dataclass(frozen=True)
class SkippedRow:
    line_number: int
    reason: str


@dataclass
class LoadResult:
    records: list[TelemetryRecord] = field(default_factory=list)
    skipped: list[SkippedRow] = field(default_factory=list)


def parse_row(row: dict[str, str | None]) -> TelemetryRecord:
    """Turn one CSV row into a TelemetryRecord. Raises ValueError if the row is bad."""
    device_id = (row.get("device_id") or "").strip()
    if not device_id:
        raise ValueError("missing device_id")

    status_text = (row.get("status") or "").strip().upper()
    try:
        status = Status(status_text)
    except ValueError:
        raise ValueError(f"invalid status {row.get('status')!r}") from None

    temperature_text = (row.get("temperature") or "").strip()
    try:
        temperature = float(temperature_text)
    except ValueError:
        raise ValueError(f"invalid temperature {temperature_text!r}") from None
    if not math.isfinite(temperature):
        raise ValueError(f"invalid temperature {temperature_text!r}")

    return TelemetryRecord(device_id=device_id, status=status, temperature=temperature)


def load_records(path: str | Path) -> LoadResult:
    """Load valid records from a telemetry CSV, skipping (and reporting) bad rows.

    Raises TelemetryFileError if the file can't be read or lacks required columns.
    """
    path = Path(path)
    result = LoadResult()

    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)

            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                raise TelemetryFileError(
                    f"{path} is missing required column(s): {', '.join(missing)}"
                )

            for row in reader:
                try:
                    result.records.append(parse_row(row))
                except ValueError as exc:
                    result.skipped.append(SkippedRow(reader.line_num, str(exc)))
    except FileNotFoundError:
        raise TelemetryFileError(f"File not found: {path}") from None
    except (IsADirectoryError, PermissionError, UnicodeDecodeError, csv.Error) as exc:
        raise TelemetryFileError(f"Could not read {path}: {exc}") from exc

    return result
