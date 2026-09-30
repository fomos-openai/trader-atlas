from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from trader_atlas.cli import main

ROOT = Path(__file__).resolve().parents[2]


class ResearchCliTests(unittest.TestCase):
    def test_research_emits_approved_cost_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = main(
                [
                    "research",
                    "--config",
                    str(ROOT / "configs/btc-eth-spot-trend.yml"),
                    "--data",
                    str(ROOT / "tests/fixtures/btc-eth-daily-synthetic.csv"),
                    "--output-root",
                    directory,
                    "--run-id",
                    "research-cli",
                ]
            )
            self.assertEqual(result, 0)
            metrics = json.loads(
                (Path(directory) / "research-cli/metrics.json").read_text(encoding="utf-8")
            )
        self.assertEqual(
            list(metrics["strategy"]),
            ["base_15bp", "stress_25bp", "stress_40bp"],
        )


if __name__ == "__main__":
    unittest.main()
