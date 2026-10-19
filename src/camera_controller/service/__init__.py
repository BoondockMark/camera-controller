from __future__ import annotations

from pathlib import Path

from ..config import CameraControllerSettings
from ..models import CameraInfo


class SessionManager:
    """Thin convenience wrapper around orchestrator logic."""

    def __init__(self, settings: CameraControllerSettings) -> None:
        self.settings = settings

    def build_session_root(self, session_id: str) -> Path:
        root = Path(self.settings.ingest_root) / session_id
        root.mkdir(parents=True, exist_ok=True)
        return root

    def register_camera(self, camera: CameraInfo) -> CameraInfo:
        return camera
