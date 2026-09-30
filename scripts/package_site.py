#!/usr/bin/env python3
"""Package root release artifacts into an already-built MkDocs site."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_exact(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Required release artifact is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    if digest(source) != digest(destination):
        raise RuntimeError(f"SHA-256 mismatch after packaging {source}")


def package(site_dir: Path) -> None:
    if not site_dir.is_dir():
        raise FileNotFoundError(
            f"MkDocs output does not exist: {site_dir}. Run mkdocs build first."
        )
    copy_exact(ROOT / "00-knowledge-map.html", site_dir / "knowledge-map/index.html")
    copy_exact(
        ROOT / "output/pdf/trader-atlas.pdf",
        site_dir / "downloads/trader-atlas.pdf",
    )
    (site_dir / ".nojekyll").touch()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    package(args.site_dir.resolve())
    print(args.site_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
