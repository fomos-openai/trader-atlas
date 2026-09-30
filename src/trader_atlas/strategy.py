from __future__ import annotations

import math

import numpy as np
import pandas as pd

from trader_atlas.config import AppConfig
from trader_atlas.portfolio import volatility_target_weight

DECISION_COLUMNS = (
    "decision_timestamp",
    "signal_as_of",
    "selected_symbol",
    "target_weight",
    "reason",
    "selected_volatility",
    "btc_momentum",
    "eth_momentum",
    "btc_sma",
    "eth_sma",
    "btc_close",
    "eth_close",
)


def _safe_float(value: float) -> float | None:
    return float(value) if math.isfinite(float(value)) else None


def compute_decisions(frame: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    symbols = config.universe.symbols
    closes = frame.pivot(index="timestamp", columns="symbol", values="close")
    closes = closes.loc[:, list(symbols)].sort_index()
    dates = closes.index
    previous_selection: str | None = None
    records: list[dict[str, object]] = []

    for position, decision_time in enumerate(dates):
        if decision_time.weekday() != config.strategy.rebalance_weekday:
            continue

        history = closes.iloc[:position]
        base: dict[str, object] = {
            "decision_timestamp": decision_time,
            "signal_as_of": history.index[-1] if not history.empty else pd.NaT,
            "selected_symbol": None,
            "target_weight": 0.0,
            "reason": "warmup",
            "selected_volatility": None,
        }
        diagnostics: dict[str, float | None] = {}
        for prefix in ("btc", "eth"):
            diagnostics[f"{prefix}_momentum"] = None
            diagnostics[f"{prefix}_sma"] = None
            diagnostics[f"{prefix}_close"] = None

        if len(history) < config.warmup_bars:
            records.append({**base, **diagnostics})
            continue

        momentums: dict[str, float] = {}
        eligible: list[str] = []
        for prefix, symbol in zip(("btc", "eth"), symbols, strict=True):
            series = history[symbol]
            latest_close = float(series.iloc[-1])
            momentum = latest_close / float(series.iloc[-(config.strategy.momentum_days + 1)]) - 1.0
            sma = float(series.iloc[-config.strategy.sma_days :].mean())
            momentums[symbol] = momentum
            diagnostics[f"{prefix}_momentum"] = momentum
            diagnostics[f"{prefix}_sma"] = sma
            diagnostics[f"{prefix}_close"] = latest_close
            if latest_close > sma and momentum > 0.0:
                eligible.append(symbol)

        if not eligible:
            base["reason"] = "no_eligible_trend"
            previous_selection = None
            records.append({**base, **diagnostics})
            continue

        top_score = max(momentums[symbol] for symbol in eligible)
        tied = [symbol for symbol in eligible if momentums[symbol] == top_score]
        if previous_selection in tied:
            selected = previous_selection
        else:
            selected = sorted(tied, key=lambda item: symbols.index(item))[0]

        volatility_history = history[selected].iloc[-(config.strategy.volatility_days + 1) :]
        log_returns = np.log(volatility_history / volatility_history.shift(1)).dropna()
        annualized_volatility = float(
            log_returns.std(ddof=1) * math.sqrt(config.strategy.annualization_days)
        )
        if not math.isfinite(annualized_volatility) or annualized_volatility <= 0.0:
            base["reason"] = "invalid_volatility"
            previous_selection = None
            records.append({**base, **diagnostics})
            continue

        target_weight = volatility_target_weight(
            target_annual_volatility=config.strategy.target_annual_volatility,
            estimated_annual_volatility=annualized_volatility,
            maximum_weight=config.strategy.max_weight,
        )
        base.update(
            {
                "selected_symbol": selected,
                "target_weight": target_weight,
                "reason": "trend_selected",
                "selected_volatility": annualized_volatility,
            }
        )
        previous_selection = selected
        records.append({**base, **diagnostics})

    decisions = pd.DataFrame.from_records(records, columns=DECISION_COLUMNS)
    if not decisions.empty:
        decisions["decision_timestamp"] = pd.to_datetime(decisions["decision_timestamp"], utc=True)
        decisions["signal_as_of"] = pd.to_datetime(decisions["signal_as_of"], utc=True)
    return decisions
