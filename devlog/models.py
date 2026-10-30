"""Data models shared across the pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    ACTIVE = "ACTIVE"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class TelemetryRecord:
    device_id: str
    status: Status
    temperature: float
