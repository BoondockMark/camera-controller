from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal


@dataclass(slots=True)
class CameraInfo:
    """Metadata describing a discovered camera."""

    name: str
    ip_address: str
    model: str = "Canon"
    serial: str | None = None
    port: int = 80
    is_online: bool = True
    last_seen: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class CameraState:
    """Device state for a Canon camera."""

    shutter_speed: str | None = None
    iso: int | None = None
    aperture: str | None = None
    exposure_mode: str | None = None
    white_balance: str | None = None
    recording: bool = False


@dataclass(slots=True)
class RecordingSession:
    """Session metadata for a synchronized capture run."""

    session_id: str
    camera_ids: list[str]
    started_at: datetime | None = None
    ended_at: datetime | None = None
    status: Literal["created", "active", "stopped", "failed"] = "created"
    local_root: Path | None = None


@dataclass(slots=True)
class TransferResult:
    """Outcome for a single media transfer."""

    source_path: str
    destination_path: str
    checksum_ok: bool = False
    transferred_at: datetime = field(default_factory=datetime.utcnow)
