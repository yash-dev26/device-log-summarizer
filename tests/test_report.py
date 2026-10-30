from devlog.models import DeviceSummary
from devlog.report import format_table


def test_table_has_headers_separator_and_aligned_rows():
    table = format_table(
        [
            DeviceSummary("DEV_A", 4, 56.375, 1),
            DeviceSummary("DEV_LONG_NAME", 12, 31.85, 10),
        ]
    )
    lines = table.splitlines()

    assert lines[0].split() == ["Device", "Records", "Avg", "Temp", "Errors"]
    assert set(lines[1].replace(" ", "")) == {"-"}
    assert "56.38" in lines[2] or "56.37" in lines[2]
    assert "31.85" in lines[3]
    assert len({len(line) for line in lines}) == 1  # every line has the same width


def test_empty_table_shows_message():
    assert format_table([]) == "No devices to display."
