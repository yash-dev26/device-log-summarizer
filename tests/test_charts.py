import json

import pytest

from devlog.charts import ChartError, build_figure, load_summary, main, plot_avg_temperature
from devlog.export import write_json
from devlog.models import DeviceSummary

DEVICES = [
    {"device_id": "DEV_A", "avg_temperature": 56.38},
    {"device_id": "DEV_B", "avg_temperature": 31.85},
]


def make_summary_file(tmp_path):
    path = tmp_path / "summary.json"
    write_json([DeviceSummary("DEV_A", 4, 56.375, 1), DeviceSummary("DEV_B", 4, 31.85, 1)], path)
    return path


# --- loading (no matplotlib needed) ---------------------------------------


def test_load_summary_reads_devices(tmp_path):
    devices = load_summary(make_summary_file(tmp_path))
    assert [d["device_id"] for d in devices] == ["DEV_A", "DEV_B"]
    assert devices[0]["avg_temperature"] == 56.38


def test_load_summary_missing_file(tmp_path):
    with pytest.raises(ChartError, match="not found"):
        load_summary(tmp_path / "nope.json")


def test_load_summary_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ChartError, match="Could not read"):
        load_summary(path)


def test_load_summary_wrong_structure(tmp_path):
    path = tmp_path / "wrong.json"
    path.write_text(json.dumps({"devices": [{"device_id": "DEV_A"}]}), encoding="utf-8")
    with pytest.raises(ChartError, match="not a valid summary"):
        load_summary(path)


# --- plotting (skipped if matplotlib isn't installed) ---------------------


def test_figure_has_title_axis_labels_and_one_bar_per_device():
    pytest.importorskip("matplotlib")
    import matplotlib.pyplot as plt

    fig = build_figure(DEVICES)
    ax = fig.axes[0]
    try:
        assert ax.get_title()
        assert ax.get_xlabel()
        assert ax.get_ylabel()
        assert len(ax.patches) == len(DEVICES)
        assert all(label.get_rotation() == 45 for label in ax.get_xticklabels())
    finally:
        plt.close(fig)


def test_plot_writes_png_and_creates_folders(tmp_path):
    pytest.importorskip("matplotlib")
    out = plot_avg_temperature(DEVICES, tmp_path / "charts" / "chart.png")

    assert out.read_bytes().startswith(b"\x89PNG")


def test_plot_with_no_devices_raises():
    pytest.importorskip("matplotlib")
    with pytest.raises(ChartError, match="No devices"):
        build_figure([])


def test_main_end_to_end(tmp_path, capsys):
    pytest.importorskip("matplotlib")
    out = tmp_path / "chart.png"

    assert main([str(make_summary_file(tmp_path)), "-o", str(out)]) == 0
    assert out.exists()
    assert "Saved chart" in capsys.readouterr().out


def test_main_missing_input_returns_1(tmp_path, capsys):
    assert main([str(tmp_path / "nope.json"), "-o", str(tmp_path / "c.png")]) == 1
    assert "error:" in capsys.readouterr().err
