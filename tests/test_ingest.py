from pathlib import Path

import pytest

from devlog.ingest import TelemetryFileError, load_records
from devlog.models import Status

SAMPLE_CSV = Path(__file__).parent.parent / "data" / "device_telemetry.csv"


def write_csv(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "telemetry.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_valid_rows(tmp_path):
    path = write_csv(tmp_path, "device_id,status,temperature\nDEV_A,ACTIVE,45.5\nDEV_B,ERROR,90\n")
    result = load_records(path)

    assert len(result.records) == 2
    assert result.records[0].device_id == "DEV_A"
    assert result.records[0].status is Status.ACTIVE
    assert result.records[0].temperature == 45.5
    assert result.skipped == []


def test_normalizes_whitespace_and_status_case(tmp_path):
    path = write_csv(tmp_path, "device_id,status,temperature\n DEV_A , warning , 50.0 \n")
    record = load_records(path).records[0]

    assert record.device_id == "DEV_A"
    assert record.status is Status.WARNING
    assert record.temperature == 50.0


def test_bad_rows_are_skipped_with_line_numbers_and_reasons(tmp_path):
    path = write_csv(
        tmp_path,
        "device_id,status,temperature\n"
        "DEV_A,ACTIVE,40\n"
        "DEV_A,ACTIVE,hot\n"
        "DEV_A,ACTIVE,nan\n"
        "DEV_A,BROKEN,40\n"
        ",ACTIVE,40\n"
        "DEV_A,ACTIVE\n",
    )
    result = load_records(path)

    assert len(result.records) == 1
    assert [s.line_number for s in result.skipped] == [3, 4, 5, 6, 7]
    assert "temperature" in result.skipped[0].reason
    assert "status" in result.skipped[2].reason
    assert "device_id" in result.skipped[3].reason


def test_missing_file_raises_clear_error(tmp_path):
    with pytest.raises(TelemetryFileError, match="not found"):
        load_records(tmp_path / "nope.csv")


def test_missing_required_column_raises(tmp_path):
    path = write_csv(tmp_path, "device_id,status\nDEV_A,ACTIVE\n")
    with pytest.raises(TelemetryFileError, match="temperature"):
        load_records(path)


def test_empty_file_raises(tmp_path):
    with pytest.raises(TelemetryFileError):
        load_records(write_csv(tmp_path, ""))


def test_sample_data_file_loads_with_expected_counts():
    result = load_records(SAMPLE_CSV)

    assert len(result.records) == 14
    assert len(result.skipped) == 4
