from __future__ import annotations

import argparse
from pathlib import Path

from .cameras import CanonCameraController, NetworkCameraDiscovery, UsbCanonCameraController, UsbCameraDiscovery
from .config import CameraControllerSettings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Canon camera controller service")
    parser.add_argument("--transport", choices=("usb", "network"), default="usb", help="Preferred transport for camera control")
    parser.add_argument("--network", default="192.168.1.0/24", help="Local network to scan for cameras when using network transport")
    parser.add_argument("--ingest-root", type=Path, default=Path("sessions"), help="Directory for downloaded media")

    subparsers = parser.add_subparsers(dest="command")

    discover = subparsers.add_parser("discover", help="Search for camera devices")
    discover.add_argument("--timeout", type=float, default=0.7, help="Legacy HTTP timeout per network probe")

    session = subparsers.add_parser("session", help="Manage a recording session")
    session.add_argument("--camera", help="Camera identifier or device path to act on")
    session.add_argument("--start-recording", action="store_true", help="Start recording on the target camera")
    session.add_argument("--stop-recording", action="store_true", help="Stop recording on the target camera")
    session.add_argument("--set-shutter", help="Set a shutter value such as 1/60")
    session.add_argument("--set-iso", type=int, help="Set ISO value")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    settings = CameraControllerSettings(
        network=args.network,
        ingest_root=args.ingest_root,
        transport=args.transport,
    )

    if args.command == "discover":
        if args.transport == "network":
            discovery = NetworkCameraDiscovery(settings)
            cameras = discovery.discover_cameras(timeout=args.timeout)
            if not cameras:
                print("No network cameras discovered.")
                return 0
            for camera in cameras:
                print(f"{camera.label} | {camera.ip_address} | model={camera.model or 'unknown'} | canon={camera.is_likely_canon}")
            return 0

        discovery = UsbCameraDiscovery(settings)
        cameras = discovery.discover_cameras()
        if not cameras:
            print("No USB cameras detected. Connect a supported Canon camera via USB and ensure the Canon driver stack is available.")
            return 0
        for camera in cameras:
            print(f"{camera.label} | {camera.camera_id} | model={camera.model or 'unknown'} | transport={camera.transport}")
        return 0

    if args.command == "session":
        if not args.camera:
            print("A --camera identifier is required for session commands.")
            return 2

        controller = UsbCanonCameraController(args.camera) if args.transport == "usb" else CanonCameraController(args.camera)
        if args.set_shutter:
            controller.connect()
            print(f"Set shutter: {controller.set_state(shutter_speed=args.set_shutter)}")
        if args.set_iso is not None:
            controller.connect()
            print(f"Set ISO: {controller.set_state(iso=args.set_iso)}")
        if args.start_recording:
            controller.connect()
            print(f"Start recording: {controller.start_recording()}")
        if args.stop_recording:
            controller.connect()
            print(f"Stop recording: {controller.stop_recording()}")
        if not any([args.start_recording, args.stop_recording, args.set_shutter is not None, args.set_iso is not None]):
            print(f"Session command received for {args.camera} but no action was specified.")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
