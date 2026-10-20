from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class UsbCameraDescriptor:
    """Descriptor for a connected USB Canon camera."""

    camera_id: str
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    device_path: str | None = None
    bus_id: str | None = None
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    transport: str = "usb"

    @property
    def label(self) -> str:
        return self.model or self.camera_id or "Canon camera"


class UsbCameraDiscovery:
    """USB discovery using Canon-compatible device enumeration.

    This intentionally fails safely when no USB stack is present so the service can stay
    honest about what it can actually control.
    """

    CANON_VID = 0x04A9

    def __init__(self, settings: Any | None = None) -> None:
        self.settings = settings

    def discover_cameras(self) -> list[UsbCameraDescriptor]:
        try:
            import usb.core  # type: ignore
        except Exception:
            return []

        discovered: list[UsbCameraDescriptor] = []
        try:
            for device in usb.core.find(find_all=True):
                if device.idVendor != self.CANON_VID:
                    continue
                descriptor = UsbCameraDescriptor(
                    camera_id=f"canon-usb-{device.idVendor:04x}-{device.idProduct:04x}",
                    manufacturer="Canon",
                    model=getattr(device, "product", None) or "Canon camera",
                    serial_number=getattr(device, "serial_number", None),
                    device_path=str(getattr(device, "bus", None)) + ":" + str(getattr(device, "address", None)),
                    bus_id=str(getattr(device, "bus", None)),
                    transport="usb",
                )
                discovered.append(descriptor)
        except Exception:
            return []
        return discovered
