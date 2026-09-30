from __future__ import annotations

import math

import pandas as pd


def synthetic_market_data(days: int = 460) -> pd.DataFrame:
    """Return deterministic, continuous daily BTC/ETH bars with regime changes."""

    if days < 230:
        raise ValueError("fixture must cover the 200-day warm-up plus evaluation")
    dates = pd.date_range("2020-01-01", periods=days, freq="D", tz="UTC")
    records: list[dict[str, object]] = []
    previous = {"BTC": 100.0, "ETH": 80.0}

    for index, timestamp in enumerate(dates):
        if index < 285:
            btc_log = math.log(100.0) + 0.0030 * index + 0.025 * math.sin(index / 11)
            eth_log = math.log(80.0) + 0.0015 * index + 0.020 * math.sin(index / 9)
        else:
            btc_anchor = math.log(100.0) + 0.0030 * 285
            eth_anchor = math.log(80.0) + 0.0015 * 285
            btc_log = btc_anchor - 0.0020 * (index - 285) + 0.020 * math.sin(index / 11)
            eth_log = eth_anchor + 0.0040 * (index - 285) + 0.020 * math.sin(index / 9)

        closes = {"BTC": math.exp(btc_log), "ETH": math.exp(eth_log)}
        for symbol in ("BTC", "ETH"):
            gap = 1.0 + 0.0015 * math.sin((index + (0 if symbol == "BTC" else 3)) / 5)
            opening = previous[symbol] * gap
            closing = closes[symbol]
            records.append(
                {
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "open": opening,
                    "high": max(opening, closing) * 1.01,
                    "low": min(opening, closing) * 0.99,
                    "close": closing,
                    "volume": 1_000.0 + index * 2 + (0 if symbol == "BTC" else 500),
                }
            )
            previous[symbol] = closing
    return pd.DataFrame.from_records(records)
