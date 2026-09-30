from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.synthetic import synthetic_market_data
from trader_atlas.config import load_config
from trader_atlas.data_contract import validate_market_data
from trader_atlas.signals import compute_decisions

ROOT = Path(__file__).resolve().parents[2]


class NoLookaheadTests(unittest.TestCase):
    def test_future_prices_cannot_change_existing_decision(self) -> None:
        config, _ = load_config(ROOT / "configs/btc-eth-spot-trend.yml")
        raw = synthetic_market_data()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "market.csv"
            raw.to_csv(source, index=False)
            frame, _ = validate_market_data(raw, source, config)
        baseline = compute_decisions(frame, config)
        chosen = baseline[baseline["reason"] != "warmup"].iloc[4]
        changed = frame.copy()
        future = changed["timestamp"] >= chosen["decision_timestamp"]
        changed.loc[future, ["open", "high", "low", "close"]] *= 100.0
        repeated = compute_decisions(changed, config)
        observed = repeated[repeated["decision_timestamp"] == chosen["decision_timestamp"]].iloc[0]
        self.assertEqual(chosen["selected_symbol"], observed["selected_symbol"])
        self.assertEqual(chosen["target_weight"], observed["target_weight"])
        self.assertLess(chosen["signal_as_of"], chosen["decision_timestamp"])


if __name__ == "__main__":
    unittest.main()
