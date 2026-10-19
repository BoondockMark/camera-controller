from __future__ import annotations

from pathlib import Path

import httpx

from ..models import CameraState
from .base import CameraControllerProtocol


class CanonCameraController(CameraControllerProtocol):
    """Generic Canon camera control adapter built around the HTTP API pattern used by Canon devices."""

    def __init__(self, ip_address: str, *, timeout: float = 5.0, api_root: str | None = None) -> None:
        self.ip_address = ip_address
        self.timeout = timeout
        self.api_root = api_root or f"http://{ip_address}/ccapi/ver100"
        self.connected = False
        self._last_state = CameraState()
        self._client = httpx.Client(timeout=timeout)

    def connect(self) -> bool:
        try:
            response = self._client.get(self.api_root.rstrip("/") + "/", follow_redirects=True)
            self.connected = response.status_code < 500
            return self.connected
        except (httpx.HTTPError, OSError):
            self.connected = False
            return False

    def disconnect(self) -> None:
        self.connected = False
        self._client.close()

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
        if not self.connected:
            return False

        payload = {
            "shutter_speed": shutter_speed,
            "iso": iso,
            "aperture": aperture,
            "exposure_mode": exposure_mode,
        }
        payload = {key: value for key, value in payload.items() if value is not None}

        try:
            response = self._client.post(
                self.api_root.rstrip("/") + "/camera/control",
                json=payload,
                follow_redirects=True,
            )
        except (httpx.HTTPError, OSError):
            return False

        if response.status_code in {200, 202, 204}:
            self._last_state.shutter_speed = shutter_speed or self._last_state.shutter_speed
            self._last_state.iso = iso if iso is not None else self._last_state.iso
            self._last_state.aperture = aperture or self._last_state.aperture
            self._last_state.exposure_mode = exposure_mode or self._last_state.exposure_mode
            return True
        return False

    def start_recording(self) -> bool:
        if not self.connected:
            return False
        try:
            response = self._client.post(
                self.api_root.rstrip("/") + "/camera/recording",
                json={"recording": True},
                follow_redirects=True,
            )
        except (httpx.HTTPError, OSError):
            return False
        if response.status_code in {200, 202, 204}:
            self._last_state.recording = True
            return True
        return False

    def stop_recording(self) -> bool:
        if not self.connected:
            return False
        try:
            response = self._client.post(
                self.api_root.rstrip("/") + "/camera/recording",
                json={"recording": False},
                follow_redirects=True,
            )
        except (httpx.HTTPError, OSError):
            return False
        if response.status_code in {200, 202, 204}:
            self._last_state.recording = False
            return True
        return False

    def list_media(self) -> list[str]:
        return []

    def download_media(self, remote_path: str, destination_dir: Path) -> Path:
        destination_dir = Path(destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / Path(remote_path).name
        try:
            with self._client.stream("GET", self.api_root.rstrip("/") + "/media/" + remote_path.lstrip("/")) as response:
                response.raise_for_status()
                with destination.open("wb") as fh:
                    for chunk in response.iter_bytes():
                        fh.write(chunk)
        except (httpx.HTTPError, OSError):
            raise
        return destination
