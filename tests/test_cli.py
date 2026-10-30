import json
from pathlib import Path

from devlog.cli import main

SAMPLE_CSV = Path(__file__).parent.parent / "data" / "device_telemetry.csv"


def test_end_to_end_writes_json_and_prints_table(tmp_path, capsys):
    out = tmp_path / "result.json"
    code = main([str(SAMPLE_CSV), "-o", str(out)])
    captured = capsys.readouterr()

    assert code == 0
    devices = json.loads(out.read_text(encoding="utf-8"))["devices"]
    assert [d["device_id"] for d in devices] == ["DEV_A", "DEV_B", "DEV_D"]
    assert "DEV_A" in captured.out
    assert "Filtered out 1 device(s)" in captured.out
    assert "DEV_C" in captured.out.split("Filtered out")[1]


def test_skipped_rows_are_reported_on_stderr(tmp_path, capsys):
    main([str(SAMPLE_CSV), "-o", str(tmp_path / "out.json")])
    assert capsys.readouterr().err.count("warning: skipped line") == 4


def test_missing_input_file_returns_1_and_writes_nothing(tmp_path, capsys):
    out = tmp_path / "out.json"
    code = main([str(tmp_path / "nope.csv"), "-o", str(out)])

    assert code == 1
    assert "not found" in capsys.readouterr().err
    assert not out.exists()


def test_max_avg_option_changes_the_filter(tmp_path):
    out = tmp_path / "out.json"
    assert main([str(SAMPLE_CSV), "-o", str(out), "--max-avg", "90"]) == 0

    devices = json.loads(out.read_text(encoding="utf-8"))["devices"]
    assert [d["device_id"] for d in devices] == ["DEV_A", "DEV_B", "DEV_C", "DEV_D"]


def test_unwritable_output_path_returns_1(tmp_path, capsys):
    code = main([str(SAMPLE_CSV), "-o", str(tmp_path)])  # a directory, not a file

    assert code == 1
    assert "could not write" in capsys.readouterr().err


def test_header_only_csv_succeeds_with_empty_result(tmp_path, capsys):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("device_id,status,temperature\n", encoding="utf-8")
    out = tmp_path / "out.json"

    assert main([str(csv_path), "-o", str(out)]) == 0
    assert "No devices to display." in capsys.readouterr().out
    assert json.loads(out.read_text(encoding="utf-8")) == {"devices": []}
