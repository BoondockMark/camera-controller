"""Camera discovery helpers and LAN probing logic."""

from __future__ import annotations

import ipaddress
from typing import Iterable

import httpx

from ..config import CameraControllerSettings
from ..models import CameraInfo


class NetworkCameraDiscovery:
    """Simple LAN discovery for Canon cameras using HTTP probes."""

    def __init__(self, settings: CameraControllerSettings) -> None:
        self.settings = settings
        self.network = ipaddress.ip_network(settings.network, strict=False)

    def discover_cameras(self, timeout: float = 0.7) -> list[CameraInfo]:
        """Probe each address in the local network and return likely camera devices."""
        discovered: list[CameraInfo] = []
        for ip in self._iter_network_addresses():
            if not self._looks_like_camera(ip, timeout=timeout):
                continue
            discovered.append(
                CameraInfo(
                    name=f"canon-camera-{ip}",
                    ip_address=str(ip),
                    model="Canon",
                    port=self.settings.default_camera_port,
                    is_online=True,
                )
            )
        return discovered

    def _iter_network_addresses(self) -> Iterable[ipaddress.IPv4Address]:
        for ip in self.network.hosts():
            yield ip

    def _looks_like_camera(self, ip: ipaddress.IPv4Address, timeout: float) -> bool:
        url = f"http://{ip}:{self.settings.default_camera_port}/"
        try:
            response = httpx.get(url, timeout=timeout)
            if response.status_code < 500:
                return True
        except (httpx.HTTPError, OSError):
            return False
        return False
