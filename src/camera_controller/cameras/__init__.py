from __future__ import annotations

import ipaddress
import json
import re
from typing import Any, Iterable

import httpx

from ..config import CameraControllerSettings
from .identity import CanonDeviceIdentity


class NetworkCameraDiscovery:
    """LAN discovery and identity probing for Canon cameras."""

    def __init__(self, settings: CameraControllerSettings) -> None:
        self.settings = settings
        self.network = ipaddress.ip_network(settings.network, strict=False)

    def discover_cameras(self, timeout: float = 0.7) -> list[CanonDeviceIdentity]:
        """Probe each host in the configured network and return any likely Canon devices."""
        discovered: list[CanonDeviceIdentity] = []
        for ip in self._iter_network_addresses():
            identity = self.probe_identity(str(ip), timeout=timeout)
            if identity is not None and identity.is_likely_canon:
                discovered.append(identity)
        return discovered

    def probe_identity(self, ip: str, timeout: float = 0.7) -> CanonDeviceIdentity | None:
        """Attempt to identify a camera at the given IP address."""
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
            # If the provided network is malformed, return an empty result instead of crashing.
            return

    def _parse_identity(self, ip: str, response: httpx.Response) -> CanonDeviceIdentity | None:
        body = response.text or ""
        headers = {k: v for k, v in response.headers.items()}
        score = 0

        parsed: dict[str, Any] = {}
        try:
            candidate = json.loads(body)
            if isinstance(candidate, dict):
                parsed = candidate
        except json.JSONDecodeError:
            parsed = {}

        manufacturer = self._first_present_value(parsed, ["manufacturer", "Manufacturer", "brand", "Brand"])
        model = self._first_present_value(parsed, ["model", "Model", "cameraModel", "cameraModelName", "deviceModel"])
        friendly_name = self._first_present_value(parsed, ["friendlyName", "friendly_name", "name", "Name"])
        serial_number = self._first_present_value(parsed, ["serialNumber", "serial_number", "serial", "Serial"])

        for token in ("Canon", "EOS", "camera", "R6", "R5", "DIGIC"):
            if token.lower() in body.lower() or token.lower() in str(headers).lower():
                score += 1

        if manufacturer:
            score += 1
        if model:
            score += 1
        if friendly_name:
            score += 1
        if serial_number:
            score += 1

        is_likely_canon = bool(score >= 2) and bool(
            any(token.lower() in body.lower() for token in ("canon", "eos", "camera", "canon camera"))
            or response.headers.get("Server", "").lower().find("canon") >= 0
        )

        if not is_likely_canon and not model and not manufacturer and not friendly_name:
            return None

        endpoint_candidates = self._collect_endpoints(body)
        return CanonDeviceIdentity(
            ip_address=ip,
            discovered_at=__import__("datetime").datetime.utcnow(),
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

    def _first_present_value(self, payload: dict[str, Any], keys: list[str]) -> str | None:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, (int, float)):
                return str(value)
        return None

    def _collect_endpoints(self, body: str) -> list[str]:
        endpoints: list[str] = []
        for match in re.findall(r"(/[^\s\"'<>]+)", body):
            if match.startswith("/") and len(match) > 1:
                endpoints.append(match)
        return list(dict.fromkeys(endpoints))[:10]


__all__ = ["NetworkCameraDiscovery", "CanonDeviceIdentity"]
