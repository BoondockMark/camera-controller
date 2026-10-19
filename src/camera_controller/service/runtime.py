from __future__ import annotations

from pathlib import Path

from ..config import CameraControllerSettings


class CameraRuntime:
    """High-level runtime wrapper for the camera controller service."""

    def __init__(self, settings: CameraControllerSettings) -> None:
        self.settings = settings
        self.root = Path(settings.ingest_root)
        self.root.mkdir(parents=True, exist_ok=True)

    def start(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
