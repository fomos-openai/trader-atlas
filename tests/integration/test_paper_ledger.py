from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from trader_atlas.cli import main

ROOT = Path(__file__).resolve().parents[2]


class PaperLedgerTests(unittest.TestCase):
    def test_paper_output_is_intent_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = main(
                [
                    "paper",
                    "--config",
                    str(ROOT / "configs/btc-eth-spot-trend.yml"),
                    "--data",
                    str(ROOT / "tests/fixtures/btc-eth-daily-synthetic.csv"),
                    "--output-root",
                    directory,
                    "--run-id",
                    "paper-ledger",
                ]
            )
            self.assertEqual(result, 0)
            run = Path(directory) / "paper-ledger"
            metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
            orders = pd.read_csv(run / "orders.csv")
        self.assertFalse(metrics["network_used"])
        self.assertFalse(metrics["fills_assumed"])
        self.assertEqual(set(orders["status"]), {"INTENT_ONLY"})


if __name__ == "__main__":
    unittest.main()
