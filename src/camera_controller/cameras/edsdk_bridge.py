from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CanonCameraHandle:
    camera_id: str
    model: str | None = None
    serial_number: str | None = None
    sdk_handle: Any | None = None


class EDSDKBridge:
    """Minimal SDK bridge for Canon EDSDK-backed USB control.

    This intentionally keeps the import and runtime detection conservative. If the Canon
    SDK is not installed, the bridge simply reports unavailable and the higher-level app
    continues without pretending to have live camera control.
    """

    def __init__(self) -> None:
        self._sdk: Any | None = None
        self._available = False
        self._load_sdk()

    def _load_sdk(self) -> None:
        try:
            # Canon's real SDK uses a native library; the exact import path varies by SDK
            # version and platform. Keep this placeholder intentionally non-destructive.
            # Example patterns:
            # import EdsSDKLib as edsdk
            # from pycanon import Canon
            self._sdk = None
            self._available = False
        except Exception:
            self._sdk = None
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def enumerate_cameras(self) -> list[CanonCameraHandle]:
        if not self._available or self._sdk is None:
            return []
        return []

    def open_camera(self, camera_id: str) -> Any | None:
        if not self._available or self._sdk is None:
            return None
        return None

    def close_camera(self, handle: Any) -> None:
        if not self._available or handle is None:
            return

    def set_iso(self, handle: Any, iso: int) -> bool:
        if not self._available or handle is None:
            return False
        return True

    def set_shutter(self, handle: Any, shutter_speed: str) -> bool:
        if not self._available or handle is None:
            return False
        return True

    def start_recording(self, handle: Any) -> bool:
        if not self._available or handle is None:
            return False
        return True

    def stop_recording(self, handle: Any) -> bool:
        if not self._available or handle is None:
            return False
        return True
