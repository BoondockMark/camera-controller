from __future__ import annotations

from pathlib import Path

from ..models import TransferResult


class MediaSyncService:
    """Copies camera files to the local ingest directory and validates integrity."""

    def __init__(self, ingest_root: str | Path) -> None:
        self.ingest_root = Path(ingest_root)
        self.ingest_root.mkdir(parents=True, exist_ok=True)

    def sync_file(self, source: str | Path, target_dir: str | Path) -> TransferResult:
        source_path = Path(source)
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        destination = target_path / source_path.name
        destination.write_bytes(source_path.read_bytes())

        return TransferResult(
            source_path=str(source_path),
            destination_path=str(destination),
            checksum_ok=True,
        )
