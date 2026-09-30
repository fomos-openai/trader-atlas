from __future__ import annotations

import hashlib
import json
import platform
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from trader_atlas import __version__
from trader_atlas.config import AppConfig


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_source_sha256() -> str:
    """Hash the runnable Python sources, including relative names and bytes."""

    package_root = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for path in sorted(package_root.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _json_default(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _json_bytes(payload: Any, *, lines: bool = False) -> bytes:
    if lines:
        rendered = "".join(
            json.dumps(item, sort_keys=True, default=_json_default) + "\n" for item in payload
        )
    else:
        rendered = (
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
                default=_json_default,
            )
            + "\n"
        )
    return rendered.encode("utf-8")


def deterministic_trial_id(
    input_sha256: str,
    resolved_config: dict[str, Any],
    mode: str,
    scenario: str,
) -> str:
    payload = _json_bytes(
        {
            "code_sha256": package_source_sha256(),
            "config": resolved_config,
            "input_sha256": input_sha256,
            "mode": mode,
            "scenario": scenario,
        }
    )
    return hashlib.sha256(payload).hexdigest()[:16]


@dataclass
class RunArtifacts:
    run_dir: Path
    command: str
    run_id: str
    started_at: str
    config: AppConfig
    config_path: Path
    config_bytes: bytes
    input_path: Path
    input_sha256: str
    audit_events: list[dict[str, Any]]

    @classmethod
    def create(
        cls,
        *,
        output_root: str | Path,
        command: str,
        run_id: str | None,
        config: AppConfig,
        config_path: str | Path,
        config_bytes: bytes,
        input_path: str | Path,
        input_sha256: str,
    ) -> RunArtifacts:
        started = datetime.now(UTC)
        if run_id is None:
            seed = f"{command}:{input_sha256}:{started.isoformat()}".encode()
            suffix = hashlib.sha256(seed).hexdigest()[:8]
            run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}-{command}-{suffix}"
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        if not run_id or any(char not in allowed for char in run_id):
            raise ValueError("run_id may contain only letters, numbers, '-' and '_'")
        run_dir = Path(output_root) / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        instance = cls(
            run_dir=run_dir,
            command=command,
            run_id=run_id,
            started_at=started.isoformat(),
            config=config,
            config_path=Path(config_path),
            config_bytes=config_bytes,
            input_path=Path(input_path),
            input_sha256=input_sha256,
            audit_events=[],
        )
        config_suffix = instance.config_path.suffix.lower()
        if config_suffix not in {".yml", ".yaml", ".toml"}:
            config_suffix = ".txt"
        instance.write_bytes(f"config_snapshot{config_suffix}", config_bytes)
        instance.audit(
            "run_started",
            {
                "command": command,
                "config_sha256": _sha256_bytes(config_bytes),
                "input_sha256": input_sha256,
            },
        )
        return instance

    def audit(self, event: str, details: dict[str, Any] | None = None) -> None:
        self.audit_events.append(
            {
                "sequence": len(self.audit_events) + 1,
                "event": event,
                "details": details or {},
            }
        )

    def write_bytes(self, relative_path: str, payload: bytes) -> Path:
        path = self.run_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return path

    def write_json(self, relative_path: str, payload: Any) -> Path:
        return self.write_bytes(relative_path, _json_bytes(payload))

    def write_jsonl(self, relative_path: str, rows: Iterable[dict[str, Any]]) -> Path:
        return self.write_bytes(relative_path, _json_bytes(list(rows), lines=True))

    def write_frame(self, relative_path: str, frame: pd.DataFrame) -> Path:
        path = self.run_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False, float_format="%.12g", lineterminator="\n")
        return path

    def finalize(self, extra_manifest: dict[str, Any]) -> Path:
        self.audit("run_completed", extra_manifest.get("summary", {}))
        self.write_jsonl("audit.jsonl", self.audit_events)

        artifact_checksums = {
            str(path.relative_to(self.run_dir)): _sha256_path(path)
            for path in sorted(self.run_dir.rglob("*"))
            if path.is_file() and path.name not in {"manifest.json", "manifest.sha256"}
        }
        manifest = {
            "schema_version": 1,
            "package_version": __version__,
            "command": self.command,
            "run_id": self.run_id,
            "started_at": self.started_at,
            "python": platform.python_version(),
            "code": {"package_source_sha256": package_source_sha256()},
            "input": {
                "path": str(self.input_path.resolve()),
                "sha256": self.input_sha256,
            },
            "config": {
                "path": str(self.config_path.resolve()),
                "sha256": _sha256_bytes(self.config_bytes),
                "resolved": self.config.as_dict(),
            },
            "artifacts": artifact_checksums,
            **extra_manifest,
        }
        manifest_path = self.write_json("manifest.json", manifest)
        self.write_bytes(
            "manifest.sha256",
            f"{_sha256_path(manifest_path)}  manifest.json\n".encode(),
        )
        return manifest_path
