from __future__ import annotations

from pathlib import Path

from ..models import CameraState
from .base import CameraControllerProtocol
from .edsdk_bridge import EDSDKBridge


class UsbCanonCameraController(CameraControllerProtocol):
    """USB-first Canon controller.

    This intentionally fails safely until a real Canon SDK / tethering stack is
    installed and the camera is accessible through the USB transport.
    """

    def __init__(self, camera_id: str, *, timeout: float = 5.0) -> None:
        self.camera_id = camera_id
        self.timeout = timeout
        self._sdk = EDSDKBridge()
        self._handle = None
        self.connected = False
        self._last_state = CameraState()

    def connect(self) -> bool:
        if not self._sdk.available:
            self.connected = False
            return False

        self._handle = self._sdk.open_camera(self.camera_id)
        self.connected = self._handle is not None
        return self.connected

    def disconnect(self) -> None:
        if self._handle is not None:
            self._sdk.close_camera(self._handle)
            self._handle = None
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
        if not self.connected or self._handle is None:
            return False

        if iso is not None:
            if not self._sdk.set_iso(self._handle, iso):
                return False
            self._last_state.iso = iso

        if shutter_speed is not None:
            if not self._sdk.set_shutter(self._handle, shutter_speed):
                return False
            self._last_state.shutter_speed = shutter_speed

        if aperture is not None:
            self._last_state.aperture = aperture

        if exposure_mode is not None:
            self._last_state.exposure_mode = exposure_mode

        return True

    def start_recording(self) -> bool:
        if not self.connected or self._handle is None:
            return False
        ok = self._sdk.start_recording(self._handle)
        if ok:
            self._last_state.recording = True
        return ok

    def stop_recording(self) -> bool:
        if not self.connected or self._handle is None:
            return False
        ok = self._sdk.stop_recording(self._handle)
        if ok:
            self._last_state.recording = False
        return ok

    def list_media(self) -> list[str]:
        return []

    def download_media(self, remote_path: str, destination_dir: Path) -> Path:
        destination_dir = Path(destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / Path(remote_path).name
        raise NotImplementedError("USB media transfer requires the real Canon SDK or tethering stack.")
