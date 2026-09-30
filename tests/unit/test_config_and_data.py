from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from tests.synthetic import synthetic_market_data
from trader_atlas.config import load_config
from trader_atlas.data import load_and_validate, validate_market_data
from trader_atlas.errors import DataContractError

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "btc-eth-spot-trend.yml"


class ConfigAndDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config, _ = load_config(CONFIG_PATH)
        self.frame = synthetic_market_data()

    def _write_csv(self, directory: str) -> Path:
        path = Path(directory) / "market.csv"
        self.frame.to_csv(path, index=False)
        return path

    def test_approved_defaults_are_loaded(self) -> None:
        self.assertEqual(self.config.universe.symbols, ("BTC", "ETH"))
        self.assertEqual(self.config.strategy.momentum_days, 90)
        self.assertEqual(self.config.strategy.sma_days, 200)
        self.assertEqual(self.config.strategy.volatility_days, 30)
        self.assertEqual(self.config.strategy.target_annual_volatility, 0.15)
        self.assertEqual(self.config.strategy.max_weight, 0.99)
        self.assertEqual(self.config.strategy.min_rebalance_delta, 0.05)
        self.assertEqual(self.config.execution.fee_bps, 10.0)
        self.assertEqual(self.config.execution.slippage_bps, 5.0)
        self.assertEqual(
            self.config.execution.cost_scenarios_bps,
            (15.0, 25.0, 40.0),
        )
        self.assertEqual(self.config.execution.fill_method, "next_bar_open")
        self.assertTrue(self.config.paper.intent_only)

    def test_csv_contract_accepts_valid_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_csv(directory)
            normalized, report = load_and_validate(path, self.config)
        self.assertEqual(len(normalized), len(self.frame))
        self.assertEqual(report.rows_per_symbol, {"BTC": 460, "ETH": 460})
        self.assertEqual(report.timezone, "UTC")
        self.assertEqual(len(report.sha256), 64)

    def test_duplicate_and_missing_day_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = self._write_csv(directory)
            duplicate = pd.concat([self.frame, self.frame.iloc[[0]]], ignore_index=True)
            with self.assertRaisesRegex(DataContractError, "duplicate"):
                validate_market_data(duplicate, source, self.config)

            missing = self.frame.drop(index=[20, 21]).reset_index(drop=True)
            with self.assertRaisesRegex(DataContractError, "missing or non-daily"):
                validate_market_data(missing, source, self.config)

    def test_invalid_ohlc_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = self._write_csv(directory)
            broken = self.frame.copy()
            broken.loc[0, "high"] = broken.loc[0, "low"] * 0.5
            with self.assertRaisesRegex(DataContractError, "OHLC"):
                validate_market_data(broken, source, self.config)

    @unittest.skipUnless(
        importlib.util.find_spec("pyarrow") is not None,
        "pyarrow is not installed in the bundled verification runtime",
    )
    def test_parquet_contract_matches_csv_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "market.parquet"
            self.frame.to_parquet(path, index=False)
            normalized, report = load_and_validate(path, self.config)
        self.assertEqual(len(normalized), len(self.frame))
        self.assertEqual(report.format, "parquet")


if __name__ == "__main__":
    unittest.main()
