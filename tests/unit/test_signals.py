from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.synthetic import synthetic_market_data
from trader_atlas.config import load_config
from trader_atlas.data_contract import validate_market_data
from trader_atlas.signals import compute_decisions

ROOT = Path(__file__).resolve().parents[2]


class SignalTests(unittest.TestCase):
    def test_weekly_signals_are_long_or_cash_and_bounded(self) -> None:
        config, _ = load_config(ROOT / "configs/btc-eth-spot-trend.yml")
        raw = synthetic_market_data()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "market.csv"
            raw.to_csv(source, index=False)
            frame, _ = validate_market_data(raw, source, config)
        decisions = compute_decisions(frame, config)
        self.assertTrue((decisions["decision_timestamp"].dt.weekday == 0).all())
        self.assertTrue(decisions["selected_symbol"].dropna().isin(("BTC", "ETH")).all())
        self.assertTrue(decisions["target_weight"].between(0.0, 0.99).all())


if __name__ == "__main__":
    unittest.main()
