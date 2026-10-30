"""Phase 4: export aggregated results to JSON."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any

from devlog.models import DeviceSummary


def to_payload(summaries: Iterable[DeviceSummary]) -> dict[str, Any]:
    """Build the JSON-serializable structure (averages rounded to 2 decimals)."""
    devices = []
    for summary in summaries:
        entry = asdict(summary)
        entry["avg_temperature"] = round(summary.avg_temperature, 2)
        devices.append(entry)
    return {"devices": devices}


def write_json(summaries: Iterable[DeviceSummary], path: str | Path) -> None:
    """Write summaries to `path` as pretty-printed JSON, creating parent folders."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_payload(summaries), indent=2) + "\n", encoding="utf-8")
