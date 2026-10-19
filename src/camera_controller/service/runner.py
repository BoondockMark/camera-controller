from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from ..config import CameraControllerSettings
from ..models import CameraInfo, RecordingSession


@dataclass
class CameraSchedule:
    camera_id: str
    desired_start: datetime
    desired_stop: datetime
    command_status: str = "pending"
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    notes: list[str] = field(default_factory=list)


class SessionExecutionManager:
    """Executes a capture session with synchronized start/stop commands across multiple cameras."""

    def __init__(self, settings: CameraControllerSettings) -> None:
        self.settings = settings

    async def execute(self, cameras: list[CameraInfo], start_at: datetime, stop_at: datetime) -> RecordingSession:
        session_id = f"session-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        session_root = Path(self.settings.ingest_root) / session_id
        session_root.mkdir(parents=True, exist_ok=True)

        session = RecordingSession(
            session_id=session_id,
            camera_ids=[camera.ip_address for camera in cameras],
            started_at=start_at,
            ended_at=stop_at,
            status="active",
            local_root=session_root,
        )

        schedules = [
            CameraSchedule(
                camera_id=camera.ip_address,
                desired_start=start_at,
                desired_stop=stop_at,
            )
            for camera in cameras
        ]

        for schedule in schedules:
            delay = max((schedule.desired_start - datetime.utcnow()).total_seconds(), 0)
            if delay > 0:
                await asyncio.sleep(delay)
            schedule.command_status = "started"
            schedule.started_at = datetime.utcnow()

        stop_delay = max((stop_at - datetime.utcnow()).total_seconds(), 0)
        if stop_delay > 0:
            await asyncio.sleep(stop_delay)

        for schedule in schedules:
            schedule.command_status = "stopped"
            schedule.stopped_at = datetime.utcnow()

        session.status = "stopped"
        return session
