import json

from devlog.export import to_payload, write_json
from devlog.models import DeviceSummary


def test_payload_rounds_average_to_two_decimals():
    payload = to_payload([DeviceSummary("DEV_A", 4, 56.375, 1)])
    assert payload == {
        "devices": [
            {"device_id": "DEV_A", "total_records": 4, "avg_temperature": 56.38, "error_count": 1}
        ]
    }


def test_write_json_round_trips_and_creates_parent_folders(tmp_path):
    path = tmp_path / "nested" / "out.json"
    write_json([DeviceSummary("DEV_B", 2, 31.85, 0)], path)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["devices"][0]["device_id"] == "DEV_B"
    assert data["devices"][0]["avg_temperature"] == 31.85


def test_write_json_with_no_devices_writes_empty_list(tmp_path):
    path = tmp_path / "empty.json"
    write_json([], path)
    assert json.loads(path.read_text(encoding="utf-8")) == {"devices": []}
