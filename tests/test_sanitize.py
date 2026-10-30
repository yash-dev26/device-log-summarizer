from devlog.sanitize import clean_readings


def test_mixed_input_is_converted_filtered_and_clipped():
    raw = ["12.5", 7, None, "abc", -3, "-0.1", 500, 750.2, "600"]
    assert clean_readings(raw) == [12.5, 7.0, 500.0, 500.0, 500.0]


def test_empty_and_none_input_return_empty_list():
    assert clean_readings([]) == []
    assert clean_readings(None) == []


def test_all_invalid_entries_return_empty_list():
    assert clean_readings([None, "n/a", -1, "", float("nan"), float("inf")]) == []


def test_zero_is_valid_and_booleans_are_rejected():
    assert clean_readings([0, "0.0", True, False]) == [0.0, 0.0]
