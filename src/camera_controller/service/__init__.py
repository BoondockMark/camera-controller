from __future__ import annotations

from pathlib import Path

from ..config import CameraControllerSettings
from ..models import CameraInfo, RecordingSession


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

    def new_session(self, camera_ids: list[str]) -> RecordingSession:
        return RecordingSession(
            session_id=f"session-{camera_ids[0]}-{len(camera_ids)}",
            camera_ids=camera_ids,
            started_at=None,
            ended_at=None,
            status="created",
            local_root=self.build_session_root(f"session-{len(camera_ids)}"),
        )
