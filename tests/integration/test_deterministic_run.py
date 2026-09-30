from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from trader_atlas.cli import main

ROOT = Path(__file__).resolve().parents[2]


class DeterministicRunTests(unittest.TestCase):
    def test_core_outputs_match_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for run_id in ("run-a", "run-b"):
                result = main(
                    [
                        "research",
                        "--config",
                        str(ROOT / "configs/btc-eth-spot-trend.yml"),
                        "--data",
                        str(ROOT / "tests/fixtures/btc-eth-daily-synthetic.csv"),
                        "--output-root",
                        str(output),
                        "--run-id",
                        run_id,
                    ]
                )
                self.assertEqual(result, 0)
            for name in (
                "validation.json",
                "metrics.json",
                "decisions.csv",
                "equity.csv",
                "orders.csv",
                "trial_ledger.jsonl",
            ):
                self.assertEqual(
                    (output / "run-a" / name).read_bytes(),
                    (output / "run-b" / name).read_bytes(),
                    name,
                )


if __name__ == "__main__":
    unittest.main()
