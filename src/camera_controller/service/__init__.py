"""Service orchestration for synchronized capture sessions."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from ..config import CameraControllerSettings
from ..models import CameraInfo, RecordingSession


class CameraSessionOrchestrator:
    """Coordinates camera control, sync timing, and capture workflow."""

    def __init__(self, settings: CameraControllerSettings) -> None:
        self.settings = settings
        self.cameras: dict[str, CameraInfo] = {}

    def register_camera(self, camera: CameraInfo) -> None:
        self.cameras[camera.ip_address] = camera

    def start_session(self, camera_ids: Iterable[str]) -> RecordingSession:
        session = RecordingSession(
            session_id=f"session-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            camera_ids=list(camera_ids),
            started_at=datetime.utcnow(),
            status="active",
        )
        return session

    def stop_session(self, session: RecordingSession) -> RecordingSession:
        session.ended_at = datetime.utcnow()
        session.status = "stopped"
        return session

    def sync_start(self, session: RecordingSession) -> datetime:
        return datetime.utcnow()
