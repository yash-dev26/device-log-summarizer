from pathlib import Path

import pytest

from devlog.aggregate import filter_by_avg_temperature, summarize_devices
from devlog.ingest import load_records
from devlog.models import DeviceSummary, Status, TelemetryRecord

SAMPLE_CSV = Path(__file__).parent.parent / "data" / "device_telemetry.csv"


def rec(device_id: str, status: Status, temperature: float) -> TelemetryRecord:
    return TelemetryRecord(device_id, status, temperature)


def test_summarize_computes_count_mean_and_error_count():
    records = [
        rec("DEV_A", Status.ACTIVE, 40.0),
        rec("DEV_A", Status.ERROR, 60.0),
        rec("DEV_A", Status.ERROR, 50.0),
        rec("DEV_B", Status.WARNING, 30.0),
    ]
    summaries = {s.device_id: s for s in summarize_devices(records)}

    assert summaries["DEV_A"].total_records == 3
    assert summaries["DEV_A"].avg_temperature == pytest.approx(50.0)
    assert summaries["DEV_A"].error_count == 2
    assert summaries["DEV_B"].total_records == 1
    assert summaries["DEV_B"].error_count == 0


def test_summarize_is_sorted_by_device_id():
    records = [rec("DEV_B", Status.ACTIVE, 1.0), rec("DEV_A", Status.ACTIVE, 1.0)]
    assert [s.device_id for s in summarize_devices(records)] == ["DEV_A", "DEV_B"]


def test_summarize_empty_input_returns_empty_list():
    assert summarize_devices([]) == []


def test_filter_drops_above_threshold_and_keeps_exactly_80():
    summaries = [
        DeviceSummary("DEV_OK", 2, 79.9, 0),
        DeviceSummary("DEV_EDGE", 2, 80.0, 0),
        DeviceSummary("DEV_HOT", 2, 80.1, 1),
    ]
    kept = filter_by_avg_temperature(summaries)
    assert [s.device_id for s in kept] == ["DEV_OK", "DEV_EDGE"]


def test_sample_data_end_to_end_drops_dev_c():
    summaries = summarize_devices(load_records(SAMPLE_CSV).records)
    assert [s.device_id for s in summaries] == ["DEV_A", "DEV_B", "DEV_C", "DEV_D"]

    kept = {s.device_id: s for s in filter_by_avg_temperature(summaries)}
    assert sorted(kept) == ["DEV_A", "DEV_B", "DEV_D"]
    assert kept["DEV_A"].avg_temperature == pytest.approx(56.375)
    assert kept["DEV_A"].error_count == 1
    assert kept["DEV_D"].total_records == 2
