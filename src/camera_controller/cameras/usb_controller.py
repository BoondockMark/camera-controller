from __future__ import annotations

from pathlib import Path

from ..models import CameraState
from .base import CameraControllerProtocol


class UsbCanonCameraController(CameraControllerProtocol):
    """USB-first Canon controller stub.

    This intentionally fails safely until a real Canon USB/SDK stack is available.
    """

    def __init__(self, camera_id: str, *, timeout: float = 5.0) -> None:
        self.camera_id = camera_id
        self.timeout = timeout
        self.connected = False
        self._last_state = CameraState()

    def connect(self) -> bool:
        # The real Canon USB transport will be implemented by a dedicated SDK bridge.
        self.connected = False
        return False

    def disconnect(self) -> None:
        self.connected = False

    def get_state(self) -> CameraState:
        return self._last_state

    def set_state(
        self,
        *,
        shutter_speed: str | None = None,
        iso: int | None = None,
        aperture: str | None = None,
        exposure_mode: str | None = None,
    ) -> bool:
        return False

    def start_recording(self) -> bool:
        return False

    def stop_recording(self) -> bool:
        return False

    def list_media(self) -> list[str]:
        return []

    def download_media(self, remote_path: str, destination_dir: Path) -> Path:
        raise NotImplementedError("USB Canon transport requires the real Canon SDK or tethering stack.")
