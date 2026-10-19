"""Media transfer helpers for ingesting captured files from cameras."""

from __future__ import annotations

import hashlib
from pathlib import Path

from ..models import TransferResult


class MediaSyncService:
    """Handles copying camera media into a local ingest folder with validation."""

    def __init__(self, ingest_root: str | Path) -> None:
        self.ingest_root = Path(ingest_root)
        self.ingest_root.mkdir(parents=True, exist_ok=True)

    def sync_file(self, source_path: str | Path, destination_dir: str | Path) -> TransferResult:
        source = Path(source_path)
        dest_dir = Path(destination_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)

        destination = dest_dir / source.name
        destination.write_bytes(source.read_bytes())

        checksum = self._sha256(source)
        with destination.open("rb") as fh:
            dest_checksum = hashlib.sha256(fh.read()).hexdigest()

        return TransferResult(
            source_path=str(source),
            destination_path=str(destination),
            checksum_ok=(checksum == dest_checksum),
        )

    def _sha256(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
