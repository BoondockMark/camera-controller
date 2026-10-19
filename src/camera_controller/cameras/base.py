from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..models import CameraState


class CameraControllerProtocol(ABC):
    """Protocol for camera controllers; keeps the service agnostic from camera-specific logic."""

    @abstractmethod
    def connect(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> CameraState:
        raise NotImplementedError

    @abstractmethod
    def set_state(self, *, shutter_speed: str | None = None, iso: int | None = None, aperture: str | None = None, exposure_mode: str | None = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def start_recording(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def stop_recording(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_media(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def download_media(self, remote_path: str, destination_dir: Path) -> Path:
        raise NotImplementedError
