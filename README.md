# Camera Controller

A Windows-first Python background service for coordinating multiple Canon R6 Mark II cameras over a local Wi‑Fi network, with optional Bluetooth-based provisioning support.

## Project goals

- Discover Canon cameras on the local LAN
- Control camera state (shutter speed, aperture, ISO, exposure mode)
- Schedule synchronized recording start/stop across 2–3 cameras
- Transfer new media files to a local ingest folder for editing
- Keep the design extensible to additional Canon models
- Support Bluetooth-assisted Wi‑Fi setup as an optional setup path

## Architecture summary

This project is intentionally structured as a headless background service:

- `camera_controller.cameras.discovery` discovers cameras on the local network
- `camera_controller.cameras.canon_camera` is the interface to each Canon device
- `camera_controller.service.orchestrator` coordinates per-camera work and sync timing
- `camera_controller.transfers.media_sync` handles file transfer from camera to local storage
- `camera_controller.cli` exposes the startup entry points

## Current status

This repository is currently scaffolded as an initial architecture and service skeleton. It is meant to be extended into a working implementation for your Canon R6 Mark II workflow.

## Recommended workflow

1. Provision camera Wi‑Fi and assign static network settings.
2. Run the discovery service to identify cameras on the LAN.
3. Register each camera and establish a session.
4. Send exposure and shutter values for a given shot.
5. Schedule recording start and stop times with a sync tolerance of ~1–2 seconds.
6. Pull or copy media into a session folder for editing.

## Quick start

```bash
python -m venv .venv
. .venv\Scripts\activate
pip install -r requirements.txt
python -m camera_controller.cli --help
```

## Example usage

```bash
python -m camera_controller.cli discover --network 192.168.1.0/24
python -m camera_controller.cli session --camera 192.168.1.50 --start-recording
```

## Design notes

- Wi‑Fi is the primary control path.
- Bluetooth should be treated as a setup/provisioning aid rather than the primary runtime control channel.
- The initial implementation is intentionally narrow: 2–3 cameras, Windows, LAN-only, no advanced lighting analysis yet.

## Next steps

1. Add Canon HTTP API endpoint mapping for the R6 Mark II
2. Implement discovery and session registration
3. Add time-synchronized recording scheduler
4. Add file ingest and checksum validation
5. Add optional Bluetooth provisioning hooks
6. Add a future UI layer above the service
