from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class CanonDeviceIdentity:
    """Identity metadata for a discovered Canon camera."""

    ip_address: str
    discovered_at: datetime
    model: str | None = None
    manufacturer: str | None = None
    friendly_name: str | None = None
    serial_number: str | None = None
    http_status: int | None = None
    response_headers: dict[str, str] = field(default_factory=dict)
    response_body_excerpt: str = ""
    protocol: str | None = None
    endpoints: list[str] = field(default_factory=list)
    is_likely_canon: bool = False

    @property
    def label(self) -> str:
        return self.friendly_name or self.model or "Canon camera"
