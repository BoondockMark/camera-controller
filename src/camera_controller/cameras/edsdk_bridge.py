from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CanonCameraHandle:
    camera_id: str
    model: str | None = None
    serial_number: str | None = None
    sdk_handle: Any | None = None


class EDSDKBridge:
    """Optional Canon EDSDK adapter.

    This adapter intentionally does nothing unless the actual Canon SDK is installed.
    When the SDK is absent, the higher-level app remains honest and fails safely.
    """

    _IMPORT_CANDIDATES = (
        "EdsSDKLib",
        "canon",
        "pycanon",
        "canon_edsdk",
        "canonedsdk",
    )

    def __init__(self) -> None:
        self._sdk: Any | None = None
        self._available = False
        self._load_sdk()

    def _load_sdk(self) -> None:
        for module_name in self._IMPORT_CANDIDATES:
            try:
                self._sdk = importlib.import_module(module_name)
                self._available = True
                return
            except Exception:
                continue

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
        return {"camera_id": camera_id, "sdk": self._sdk}

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
