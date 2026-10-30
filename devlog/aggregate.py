"""Phase 3: group telemetry by device and filter on average temperature."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from statistics import fmean

from devlog.models import DeviceSummary, Status, TelemetryRecord

MAX_AVG_TEMPERATURE = 80.0


def summarize_devices(records: Iterable[TelemetryRecord]) -> list[DeviceSummary]:
    """Return one summary per device (record count, mean temperature, ERROR count)."""
    by_device: dict[str, list[TelemetryRecord]] = defaultdict(list)
    for record in records:
        by_device[record.device_id].append(record)

    return [
        DeviceSummary(
            device_id=device_id,
            total_records=len(group),
            avg_temperature=fmean(r.temperature for r in group),
            error_count=sum(1 for r in group if r.status is Status.ERROR),
        )
        for device_id, group in sorted(by_device.items())
    ]


def filter_by_avg_temperature(
    summaries: Iterable[DeviceSummary], max_avg: float = MAX_AVG_TEMPERATURE
) -> list[DeviceSummary]:
    """Keep devices whose average temperature is at or below `max_avg`."""
    return [s for s in summaries if s.avg_temperature <= max_avg]
