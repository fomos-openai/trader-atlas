from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from tests.synthetic import synthetic_market_data
from trader_atlas.config import load_config
from trader_atlas.data import validate_market_data
from trader_atlas.engine import build_paper_intents, simulate
from trader_atlas.metrics import simulation_metrics
from trader_atlas.strategy import compute_decisions

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "btc-eth-spot-trend.yml"


class StrategyAndEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config, _ = load_config(CONFIG_PATH)
        raw = synthetic_market_data()
        self.tempdir = tempfile.TemporaryDirectory()
        self.source = Path(self.tempdir.name) / "market.csv"
        raw.to_csv(self.source, index=False)
        self.frame, _ = validate_market_data(raw, self.source, self.config)
        self.decisions = compute_decisions(self.frame, self.config)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_signal_is_strictly_prior_to_next_bar_open(self) -> None:
        actionable = self.decisions[self.decisions["reason"] != "warmup"]
        self.assertFalse(actionable.empty)
        self.assertTrue((actionable["signal_as_of"] < actionable["decision_timestamp"]).all())

        chosen = actionable.iloc[3]
        decision_time = chosen["decision_timestamp"]
        changed = self.frame.copy()
        future = changed["timestamp"] >= decision_time
        changed.loc[future, ["open", "high", "low", "close"]] *= 50.0
        changed_decisions = compute_decisions(changed, self.config)
        changed_row = changed_decisions[
            changed_decisions["decision_timestamp"] == decision_time
        ].iloc[0]
        for column in (
            "selected_symbol",
            "target_weight",
            "btc_momentum",
            "eth_momentum",
            "btc_sma",
            "eth_sma",
        ):
            self.assertEqual(chosen[column], changed_row[column])

    def test_weights_are_bounded_and_long_or_cash(self) -> None:
        self.assertTrue((self.decisions["target_weight"] >= 0).all())
        self.assertTrue((self.decisions["target_weight"] <= self.config.strategy.max_weight).all())
        selected = self.decisions[self.decisions["selected_symbol"].notna()]
        expected = (
            self.config.strategy.target_annual_volatility / selected["selected_volatility"]
        ).clip(upper=self.config.strategy.max_weight)
        pd.testing.assert_series_equal(
            selected["target_weight"], expected, check_names=False, check_dtype=False
        )

        result = simulate(self.frame, self.decisions, self.config, 15.0)
        simultaneous = (result.equity["btc_units"] > 1e-12) & (result.equity["eth_units"] > 1e-12)
        self.assertFalse(simultaneous.any())

    def test_simulation_is_deterministic_and_uses_current_open(self) -> None:
        first = simulate(self.frame, self.decisions, self.config, 15.0)
        second = simulate(self.frame, self.decisions, self.config, 15.0)
        assert_frame_equal(first.equity, second.equity)
        assert_frame_equal(first.orders, second.orders)
        self.assertGreater(len(first.orders), 0)

        opens = self.frame.set_index(["timestamp", "symbol"])["open"]
        for order in first.orders.itertuples(index=False):
            expected_open = opens.loc[(order.execution_timestamp, order.symbol)]
            self.assertAlmostEqual(order.reference_price, expected_open)
            self.assertLess(order.signal_as_of, order.execution_timestamp)

    def test_higher_cost_scenario_lowers_equity_and_records_costs(self) -> None:
        base = simulate(self.frame, self.decisions, self.config, 15.0)
        stressed = simulate(self.frame, self.decisions, self.config, 40.0)
        self.assertLess(stressed.equity.iloc[-1]["equity"], base.equity.iloc[-1]["equity"])
        first = base.orders.iloc[0]
        reference_notional = first["reference_price"] * first["quantity"]
        self.assertAlmostEqual(
            first["fee"],
            reference_notional * self.config.execution.fee_bps / 10_000,
        )
        self.assertAlmostEqual(
            first["slippage_cost"],
            abs(first["execution_price"] - first["reference_price"]) * first["quantity"],
        )
        self.assertAlmostEqual(
            first["total_cost"] / reference_notional,
            15.0 / 10_000,
        )
        base_metrics = simulation_metrics(base, self.config)
        stressed_metrics = simulation_metrics(stressed, self.config)
        self.assertGreater(
            stressed_metrics["total_execution_cost"],
            base_metrics["total_execution_cost"],
        )

    def test_five_percent_band_suppresses_small_same_asset_resize(self) -> None:
        dates = pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC")
        rows = []
        for timestamp in dates:
            for symbol in ("BTC", "ETH"):
                rows.append(
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "open": 100.0,
                        "high": 101.0,
                        "low": 99.0,
                        "close": 100.0,
                        "volume": 1_000.0,
                    }
                )
        frame = pd.DataFrame(rows)
        decisions = pd.DataFrame(
            [
                {
                    "decision_timestamp": dates[0],
                    "signal_as_of": dates[0] - pd.offsets.Day(1),
                    "selected_symbol": "BTC",
                    "target_weight": 0.50,
                    "reason": "trend_selected",
                },
                {
                    "decision_timestamp": dates[1],
                    "signal_as_of": dates[0],
                    "selected_symbol": "BTC",
                    "target_weight": 0.52,
                    "reason": "trend_selected",
                },
                {
                    "decision_timestamp": dates[2],
                    "signal_as_of": dates[1],
                    "selected_symbol": "BTC",
                    "target_weight": 0.60,
                    "reason": "trend_selected",
                },
            ]
        )
        result = simulate(frame, decisions, self.config, 15.0)
        order_dates = list(result.orders["execution_timestamp"])
        self.assertIn(dates[0], order_dates)
        self.assertNotIn(dates[1], order_dates)
        self.assertIn(dates[2], order_dates)

    def test_paper_mode_creates_intentions_without_fills(self) -> None:
        intents = build_paper_intents(self.decisions, self.config)
        self.assertFalse(intents.empty)
        self.assertEqual(set(intents["status"]), {"INTENT_ONLY"})
        self.assertFalse(intents["network_used"].any())
        self.assertFalse(intents["fill_assumed"].any())
        self.assertTrue((intents["signal_as_of"] < intents["intended_execution_timestamp"]).all())
        self.assertTrue((intents["target_weight"] <= 0.99).all())


if __name__ == "__main__":
    unittest.main()
