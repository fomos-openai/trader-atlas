#!/usr/bin/env python3
"""Convenience entry point for the frozen BTC/ETH research command."""

from __future__ import annotations

import argparse
from pathlib import Path

from trader_atlas.cli import main as trader_atlas_main

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/btc-eth-spot-trend.yml",
    )
    parser.add_argument("--output-root", type=Path, default=ROOT / "artifacts/runs")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    command = [
        "research",
        "--config",
        str(args.config),
        "--data",
        str(args.data),
        "--output-root",
        str(args.output_root),
    ]
    if args.run_id:
        command.extend(("--run-id", args.run_id))
    return trader_atlas_main(command)


if __name__ == "__main__":
    raise SystemExit(main())
