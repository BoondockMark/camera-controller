from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from ..config import CameraControllerSettings
from ..models import CameraInfo, RecordingSession


class CameraSessionOrchestrator:
    """Coordinates multi-camera sessions for synchronized capture and media imports."""

    def __init__(self, settings: CameraControllerSettings) -> None:
        self.settings = settings
        self.cameras: dict[str, CameraInfo] = {}
        self.sessions: dict[str, RecordingSession] = {}

    def register_camera(self, camera: CameraInfo) -> None:
        self.cameras[camera.ip_address] = camera

    def start_session(self, camera_ids: list[str]) -> RecordingSession:
        session_id = f"session-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        session = RecordingSession(
            session_id=session_id,
            camera_ids=camera_ids,
            started_at=datetime.utcnow(),
            status="active",
            local_root=Path(self.settings.ingest_root) / session_id,
        )
        self.sessions[session_id] = session
        return session

    def stop_session(self, session_id: str) -> RecordingSession:
        session = self.sessions[session_id]
        session.ended_at = datetime.utcnow()
        session.status = "stopped"
        return session

    def mark_failed(self, session_id: str, reason: str) -> RecordingSession:
        session = self.sessions[session_id]
        session.status = "failed"
        return session

    def sync_start(self, session: RecordingSession) -> datetime:
        return datetime.utcnow()
