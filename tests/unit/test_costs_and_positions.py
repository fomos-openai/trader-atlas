from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.synthetic import synthetic_market_data
from trader_atlas.backtest import simulate
from trader_atlas.config import load_config
from trader_atlas.data_contract import validate_market_data
from trader_atlas.signals import compute_decisions

ROOT = Path(__file__).resolve().parents[2]


class CostAndPositionTests(unittest.TestCase):
    def test_cost_monotonicity_and_long_only_positions(self) -> None:
        config, _ = load_config(ROOT / "configs/btc-eth-spot-trend.yml")
        raw = synthetic_market_data()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "market.csv"
            raw.to_csv(source, index=False)
            frame, _ = validate_market_data(raw, source, config)
        decisions = compute_decisions(frame, config)
        results = [simulate(frame, decisions, config, cost) for cost in (15.0, 25.0, 40.0)]
        final = [float(item.equity.iloc[-1]["equity"]) for item in results]
        self.assertGreaterEqual(final[0], final[1])
        self.assertGreaterEqual(final[1], final[2])
        for result in results:
            self.assertFalse((result.equity[["btc_units", "eth_units"]] < 0).any(axis=None))
            simultaneous = (result.equity["btc_units"] > 1e-12) & (
                result.equity["eth_units"] > 1e-12
            )
            self.assertFalse(simultaneous.any())


if __name__ == "__main__":
    unittest.main()
