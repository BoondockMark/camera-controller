from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class CameraControllerSettings(BaseModel):
    """Application configuration for the headless camera controller service."""

    ingest_root: Path = Field(default=Path("sessions"), description="Folder to receive transferred media")
    log_level: str = Field(default="INFO", description="Python logging level")
    network: str = Field(default="192.168.1.0/24", description="Local network to probe for cameras")
    sync_tolerance_seconds: float = Field(default=2.0, description="Allowed recording sync tolerance in seconds")
    default_camera_port: int = Field(default=80, description="Default HTTP port for Canon cameras")

    class Config:
        arbitrary_types_allowed = True
