from __future__ import annotations

import math
from typing import Any

import pandas as pd

from trader_atlas.config import AppConfig
from trader_atlas.engine import SimulationResult


def _json_number(value: float) -> float | None:
    return float(value) if math.isfinite(float(value)) else None


def _max_drawdown_duration(drawdowns: pd.Series) -> int:
    longest = 0
    current = 0
    for value in drawdowns:
        if value < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def curve_metrics(
    timestamps: pd.Series,
    equity: pd.Series,
    annualization_days: int,
) -> dict[str, Any]:
    clean = pd.DataFrame({"timestamp": timestamps, "equity": equity}).dropna()
    if clean.empty:
        return {}
    values = clean["equity"].astype(float)
    returns = values.pct_change().dropna()
    total_return = values.iloc[-1] / values.iloc[0] - 1.0
    elapsed_days = max(
        1.0,
        (
            pd.Timestamp(clean["timestamp"].iloc[-1]) - pd.Timestamp(clean["timestamp"].iloc[0])
        ).total_seconds()
        / 86_400.0,
    )
    years = elapsed_days / annualization_days
    cagr = (values.iloc[-1] / values.iloc[0]) ** (1.0 / years) - 1.0
    volatility = returns.std(ddof=1) * math.sqrt(annualization_days)
    sharpe = (
        returns.mean() / returns.std(ddof=1) * math.sqrt(annualization_days)
        if len(returns) > 1 and returns.std(ddof=1) > 0
        else math.nan
    )
    downside = returns[returns < 0]
    downside_deviation = downside.std(ddof=1) * math.sqrt(annualization_days)
    sortino = (
        returns.mean() * annualization_days / downside_deviation
        if len(downside) > 1 and downside_deviation > 0
        else math.nan
    )
    drawdowns = values / values.cummax() - 1.0
    max_drawdown = float(drawdowns.min())
    calmar = cagr / abs(max_drawdown) if max_drawdown < 0 else math.nan

    def expected_shortfall(level: float) -> float:
        if returns.empty:
            return math.nan
        threshold = returns.quantile(1.0 - level)
        tail = returns[returns <= threshold]
        return float(tail.mean()) if not tail.empty else math.nan

    return {
        "start": pd.Timestamp(clean["timestamp"].iloc[0]).isoformat(),
        "end": pd.Timestamp(clean["timestamp"].iloc[-1]).isoformat(),
        "observations": int(len(clean)),
        "start_equity": _json_number(values.iloc[0]),
        "end_equity": _json_number(values.iloc[-1]),
        "total_return": _json_number(total_return),
        "cagr": _json_number(cagr),
        "annualized_volatility": _json_number(volatility),
        "sharpe_zero_cash_rate": _json_number(sharpe),
        "sortino_zero_cash_rate": _json_number(sortino),
        "max_drawdown": _json_number(max_drawdown),
        "max_drawdown_duration_days": _max_drawdown_duration(drawdowns),
        "calmar": _json_number(calmar),
        "expected_shortfall_95_daily": _json_number(expected_shortfall(0.95)),
        "expected_shortfall_99_daily": _json_number(expected_shortfall(0.99)),
        "daily_return_skew": _json_number(returns.skew()),
        "daily_return_excess_kurtosis": _json_number(returns.kurt()),
    }


def simulation_metrics(
    result: SimulationResult,
    config: AppConfig,
) -> dict[str, Any]:
    evaluated = result.equity[result.equity["timestamp"] >= result.evaluation_start].copy()
    metrics = curve_metrics(
        evaluated["timestamp"],
        evaluated["equity"],
        config.strategy.annualization_days,
    )
    orders = result.orders
    total_notional = float(orders["notional"].sum()) if not orders.empty else 0.0
    average_equity = float(evaluated["equity"].mean()) if not evaluated.empty else math.nan
    metrics.update(
        {
            "scenario": result.scenario,
            "total_cost_bps": result.total_cost_bps,
            "final_equity": metrics.get("end_equity"),
            "order_count": int(len(orders)),
            "buy_count": int((orders["side"] == "BUY").sum()) if not orders.empty else 0,
            "sell_count": int((orders["side"] == "SELL").sum()) if not orders.empty else 0,
            "turnover_on_average_equity": _json_number(
                total_notional / average_equity if average_equity > 0 else math.nan
            ),
            "fees": _json_number(orders["fee"].sum()) if not orders.empty else 0.0,
            "slippage_cost": _json_number(orders["slippage_cost"].sum())
            if not orders.empty
            else 0.0,
            "total_execution_cost": _json_number(orders["total_cost"].sum())
            if not orders.empty
            else 0.0,
            "average_gross_exposure": _json_number(evaluated["gross_exposure"].mean()),
            "maximum_gross_exposure": _json_number(evaluated["gross_exposure"].max()),
            "cash_day_fraction": _json_number(evaluated["active_symbol"].isna().mean()),
        }
    )
    return metrics


def benchmark_metrics(
    frame: pd.DataFrame,
    config: AppConfig,
    start: pd.Timestamp,
) -> dict[str, Any]:
    symbols = config.universe.symbols
    opens = frame.pivot(index="timestamp", columns="symbol", values="open")
    closes = frame.pivot(index="timestamp", columns="symbol", values="close")
    opens = opens.loc[opens.index >= start, list(symbols)]
    closes = closes.loc[closes.index >= start, list(symbols)]
    if closes.empty:
        return {}

    initial = config.portfolio.initial_cash
    first_open = opens.iloc[0]
    curves = {
        "cash": pd.Series(initial, index=closes.index, dtype=float),
        f"{symbols[0].lower()}_buy_hold": initial
        * closes[symbols[0]]
        / float(first_open[symbols[0]]),
        f"{symbols[1].lower()}_buy_hold": initial
        * closes[symbols[1]]
        / float(first_open[symbols[1]]),
        "equal_weight_buy_hold": initial
        * 0.5
        * (
            closes[symbols[0]] / float(first_open[symbols[0]])
            + closes[symbols[1]] / float(first_open[symbols[1]])
        ),
    }
    return {
        name: curve_metrics(
            pd.Series(curve.index), curve.reset_index(drop=True), config.strategy.annualization_days
        )
        for name, curve in curves.items()
    }
