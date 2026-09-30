from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from trader_atlas.cli import main

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "btc-eth-spot-trend.yml"


class CliIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)
        self.input_path = ROOT / "tests" / "fixtures" / "btc-eth-daily-synthetic.csv"
        self.output_root = self.base / "runs"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _run(self, command: str, run_id: str) -> Path:
        exit_code = main(
            [
                command,
                "--data",
                str(self.input_path),
                "--config",
                str(CONFIG_PATH),
                "--output-root",
                str(self.output_root),
                "--run-id",
                run_id,
            ]
        )
        self.assertEqual(exit_code, 0)
        return self.output_root / run_id

    def test_research_writes_complete_checksummed_bundle(self) -> None:
        run = self._run("research", "integration-research")
        expected = {
            "config_snapshot.yml",
            "manifest.json",
            "manifest.sha256",
            "validation.json",
            "metrics.json",
            "decisions.csv",
            "equity.csv",
            "orders.csv",
            "audit.jsonl",
            "trial_ledger.jsonl",
        }
        self.assertTrue(expected.issubset({item.name for item in run.iterdir()}))

        manifest_bytes = (run / "manifest.json").read_bytes()
        expected_digest = hashlib.sha256(manifest_bytes).hexdigest()
        checksum = (run / "manifest.sha256").read_text().split()[0]
        self.assertEqual(checksum, expected_digest)

        manifest = json.loads(manifest_bytes)
        self.assertEqual(manifest["command"], "research")
        self.assertEqual(len(manifest["code"]["package_source_sha256"]), 64)
        for relative, digest in manifest["artifacts"].items():
            self.assertEqual(
                hashlib.sha256((run / relative).read_bytes()).hexdigest(),
                digest,
            )
        self.assertEqual(
            manifest["config"]["resolved"]["strategy"]["target_annual_volatility"],
            0.15,
        )
        trials = [
            json.loads(line) for line in (run / "trial_ledger.jsonl").read_text().splitlines()
        ]
        self.assertEqual(
            [trial["scenario"] for trial in trials],
            ["base_15bp", "stress_25bp", "stress_40bp"],
        )

        equity = pd.read_csv(run / "equity.csv")
        orders = pd.read_csv(run / "orders.csv")
        self.assertEqual(
            set(equity["scenario"]),
            {"base_15bp", "stress_25bp", "stress_40bp"},
        )
        self.assertEqual(set(orders["status"]), {"SIMULATED_FILL"})

    def test_validate_and_paper_are_offline_artifact_commands(self) -> None:
        validation = self._run("validate-data", "integration-validation")
        self.assertTrue((validation / "validation.json").is_file())

        paper = self._run("paper", "integration-paper")
        metrics = json.loads((paper / "metrics.json").read_text())
        intents = pd.read_csv(paper / "orders.csv")
        self.assertEqual(metrics["mode"], "paper_intent_only")
        self.assertFalse(metrics["network_used"])
        self.assertFalse(metrics["fills_assumed"])
        self.assertEqual(set(intents["status"]), {"INTENT_ONLY"})
        self.assertFalse(intents["network_used"].any())
        self.assertFalse(intents["fill_assumed"].any())
        self.assertNotIn("execution_price", intents.columns)


if __name__ == "__main__":
    unittest.main()
