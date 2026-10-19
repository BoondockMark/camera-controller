from __future__ import annotations

import argparse
from pathlib import Path

from .config import CameraControllerSettings
from .cameras.discovery import NetworkCameraDiscovery


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Canon camera controller service")
    parser.add_argument("--network", default="192.168.1.0/24", help="Local network to scan for cameras")
    parser.add_argument("--ingest-root", type=Path, default=Path("sessions"), help="Directory for downloaded media")
    subparsers = parser.add_subparsers(dest="command")

    discover = subparsers.add_parser("discover", help="Search the LAN for camera devices")
    discover.add_argument("--timeout", type=float, default=0.7, help="HTTP timeout per probe")

    session = subparsers.add_parser("session", help="Manage a recording session")
    session.add_argument("--camera", help="IP address or camera ID to act on")
    session.add_argument("--start-recording", action="store_true", help="Start recording on the target camera")
    session.add_argument("--stop-recording", action="store_true", help="Stop recording on the target camera")
    session.add_argument("--set-shutter", help="Set a shutter value such as 1/60")
    session.add_argument("--set-iso", type=int, help="Set ISO value")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    settings = CameraControllerSettings(network=args.network, ingest_root=args.ingest_root)

    if args.command == "discover":
        discovery = NetworkCameraDiscovery(settings)
        cameras = discovery.discover_cameras(timeout=args.timeout)
        if not cameras:
            print("No cameras discovered.")
            return 0
        for camera in cameras:
            print(f"{camera.label} | {camera.ip_address} | model={camera.model or 'unknown'} | canon={camera.is_likely_canon}")
        return 0

    if args.command == "session":
        print(f"Session command received for {args.camera or 'all cameras'}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
