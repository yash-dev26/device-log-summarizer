"""Section 1: clean and normalize raw sensor readings."""

from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any

MAX_READING = 500.0


def _to_float(value: Any) -> float | None:
    """Return a finite float for `value`, or None if it can't be converted."""
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def clean_readings(values: Iterable[Any] | None) -> list[float]:
    """Convert mixed sensor inputs into a list of valid, clipped floats.

    Rules:
      1. Convert to float; drop None, unconvertible, NaN/inf and negative values.
      2. Cap anything above MAX_READING (500.0) at MAX_READING.
      3. Empty or all-invalid input returns an empty list (never raises).
    """
    if values is None:
        return []

    cleaned: list[float] = []
    for value in values:
        number = _to_float(value)
        if number is None or number < 0:
            continue
        cleaned.append(min(number, MAX_READING))
    return cleaned
