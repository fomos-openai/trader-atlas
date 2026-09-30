"""Read-only helpers for inspecting immutable research-run artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_path(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_run_metrics(run_dir: str | Path) -> dict[str, Any]:
    """Load metrics only after the run manifest checksum has been verified."""

    directory = Path(run_dir)
    manifest = directory / "manifest.json"
    checksum = directory / "manifest.sha256"
    expected = checksum.read_text(encoding="utf-8").split()[0]
    actual = sha256_path(manifest)
    if actual != expected:
        raise ValueError(f"manifest checksum mismatch: expected {expected}, got {actual}")
    payload = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("metrics.json must contain a JSON object")
    return payload
