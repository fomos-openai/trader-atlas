#!/usr/bin/env python3
"""Validate and normalize an already-local market-data file.

This helper never downloads data. It is intentionally separate from the research
CLI so provenance collection and licensed raw data can remain outside Git.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from trader_atlas.config import load_config
from trader_atlas.data import load_and_validate

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Local CSV or Parquet input")
    parser.add_argument(
        "--destination",
        type=Path,
        required=True,
        help="Normalized .csv or .parquet destination (normally ignored by Git)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/btc-eth-spot-trend.yml",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    destination = args.destination.resolve()
    if destination.exists() and not args.overwrite:
        parser.error(f"destination exists; pass --overwrite to replace it: {destination}")
    if destination.suffix.lower() not in {".csv", ".parquet", ".pq"}:
        parser.error("destination must end in .csv, .parquet, or .pq")

    config, _ = load_config(args.config)
    frame, report = load_and_validate(args.source, config)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.suffix.lower() == ".csv":
        frame.to_csv(destination, index=False, lineterminator="\n")
    else:
        frame.to_parquet(destination, index=False)
    print(
        json.dumps(
            {
                "destination": str(destination),
                "input_sha256": report.sha256,
                "rows": report.row_count,
                "start": report.start,
                "end": report.end,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
