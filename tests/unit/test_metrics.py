from __future__ import annotations

import unittest

import pandas as pd

from trader_atlas.metrics import curve_metrics


class MetricsTests(unittest.TestCase):
    def test_metrics_report_risk_and_tail_fields(self) -> None:
        dates = pd.Series(pd.date_range("2024-01-01", periods=8, freq="D", tz="UTC"))
        equity = pd.Series([100.0, 102.0, 101.0, 104.0, 98.0, 99.0, 105.0, 106.0])
        metrics = curve_metrics(dates, equity, 365)
        for key in (
            "total_return",
            "annualized_volatility",
            "sharpe_zero_cash_rate",
            "max_drawdown",
            "expected_shortfall_95_daily",
        ):
            self.assertIn(key, metrics)
        self.assertLess(metrics["max_drawdown"], 0.0)


if __name__ == "__main__":
    unittest.main()
