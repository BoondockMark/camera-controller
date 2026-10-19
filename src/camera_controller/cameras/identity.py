from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable

import httpx

from ..config import CameraControllerSettings


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


class NetworkCameraDiscovery:
    """LAN discovery and identity probing for Canon cameras."""

    def __init__(self, settings: CameraControllerSettings) -> None:
        self.settings = settings
        self.network = ipaddress.ip_network(settings.network, strict=False)

    def discover_cameras(self, timeout: float = 0.7) -> list[CanonDeviceIdentity]:
        discovered: list[CanonDeviceIdentity] = []
        for ip in self._iter_network_addresses():
            identity = self.probe_identity(str(ip), timeout=timeout)
            if identity is not None and identity.is_likely_canon:
                discovered.append(identity)
        return discovered

    def probe_identity(self, ip: str, timeout: float = 0.7) -> CanonDeviceIdentity | None:
        urls = [
            f"http://{ip}:{self.settings.default_camera_port}/",
            f"http://{ip}/",
            f"http://{ip}:{self.settings.default_camera_port}/index.html",
        ]

        for url in urls:
            try:
                response = httpx.get(url, timeout=timeout, follow_redirects=True)
            except (httpx.HTTPError, OSError):
                continue

            if response.status_code >= 500:
                continue

            identity = self._parse_identity(ip, response)
            if identity is not None:
                return identity

        return None

    def _iter_network_addresses(self) -> Iterable[ipaddress.IPv4Address]:
        try:
            for ip in self.network.hosts():
                yield ip
        except ValueError:
            return

    def _parse_identity(self, ip: str, response: httpx.Response) -> CanonDeviceIdentity | None:
        body = response.text or ""
        headers = {key: value for key, value in response.headers.items()}
        score = 0

        parsed: dict[str, Any] = {}
        try:
            payload = json.loads(body)
            if isinstance(payload, dict):
                parsed = payload
        except json.JSONDecodeError:
            parsed = {}

        manufacturer = self._first_present_value(parsed, ["manufacturer", "Manufacturer", "brand", "Brand"])
        model = self._first_present_value(parsed, ["model", "Model", "cameraModel", "cameraModelName", "deviceModel"])
        friendly_name = self._first_present_value(parsed, ["friendlyName", "friendly_name", "name", "Name"])
        serial_number = self._first_present_value(parsed, ["serialNumber", "serial_number", "serial", "Serial"])

        if manufacturer:
            score += 1
        if model:
            score += 1
        if friendly_name:
            score += 1
        if serial_number:
            score += 1

        lower_body = body.lower()
        lower_headers = str(headers).lower()

        for token in ("canon", "eos", "camera", "r6", "r5", "digic"):
            if token in lower_body or token in lower_headers:
                score += 1

        is_likely_canon = score >= 2 and (
            any(token in lower_body for token in ("canon", "eos", "camera", "canon camera"))
            or "canon" in response.headers.get("Server", "").lower()
        )

        if not is_likely_canon and not model and not manufacturer and not friendly_name:
            return None

        endpoint_candidates = self._collect_endpoints(body)
        return CanonDeviceIdentity(
            ip_address=ip,
            discovered_at=datetime.utcnow(),
            model=model,
            manufacturer=manufacturer,
            friendly_name=friendly_name,
            serial_number=serial_number,
            http_status=response.status_code,
            response_headers=headers,
            response_body_excerpt=body[:500],
            protocol="http",
            endpoints=endpoint_candidates,
            is_likely_canon=is_likely_canon,
        )

    @staticmethod
    def _first_present_value(payload: dict[str, Any], keys: list[str]) -> str | None:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, (int, float)):
                return str(value)
        return None

    @staticmethod
    def _collect_endpoints(body: str) -> list[str]:
        endpoints: list[str] = []
        for match in re.findall(r"(/[^\s\"'<>]+)", body):
            if match.startswith("/") and len(match) > 1:
                endpoints.append(match)
        return list(dict.fromkeys(endpoints))[:10]


__all__ = ["CanonDeviceIdentity", "NetworkCameraDiscovery"]
