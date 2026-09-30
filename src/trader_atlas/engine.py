from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pandas as pd

from trader_atlas.config import AppConfig


@dataclass(frozen=True)
class SimulationResult:
    scenario: str
    total_cost_bps: float
    equity: pd.DataFrame
    orders: pd.DataFrame
    evaluation_start: pd.Timestamp


def scenario_name(total_cost_bps: float, base_total_cost_bps: float) -> str:
    is_base = math.isclose(
        total_cost_bps,
        base_total_cost_bps,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    prefix = "base" if is_base else "stress"
    return f"{prefix}_{total_cost_bps:g}bp"


def _order_record(
    *,
    scenario: str,
    sequence: int,
    decision_time: pd.Timestamp,
    signal_as_of: pd.Timestamp,
    symbol: str,
    side: str,
    quantity: float,
    reference_price: float,
    execution_price: float,
    fee: float,
) -> dict[str, Any]:
    notional = abs(quantity * execution_price)
    slippage_cost = abs(execution_price - reference_price) * abs(quantity)
    return {
        "scenario": scenario,
        "order_id": f"{scenario}-{decision_time.strftime('%Y%m%d')}-{sequence:04d}",
        "status": "SIMULATED_FILL",
        "decision_timestamp": decision_time,
        "signal_as_of": signal_as_of,
        "execution_timestamp": decision_time,
        "symbol": symbol,
        "side": side,
        "quantity": abs(quantity),
        "reference_price": reference_price,
        "execution_price": execution_price,
        "notional": notional,
        "fee": fee,
        "slippage_cost": slippage_cost,
        "total_cost": fee + slippage_cost,
    }


def simulate(
    frame: pd.DataFrame,
    decisions: pd.DataFrame,
    config: AppConfig,
    total_cost_bps: float,
) -> SimulationResult:
    if total_cost_bps < config.execution.fee_bps:
        raise ValueError("total_cost_bps cannot be lower than fee_bps")

    symbols = config.universe.symbols
    opens = frame.pivot(index="timestamp", columns="symbol", values="open")
    closes = frame.pivot(index="timestamp", columns="symbol", values="close")
    opens = opens.loc[:, list(symbols)].sort_index()
    closes = closes.loc[:, list(symbols)].sort_index()
    dates = opens.index

    decision_map = {row.decision_timestamp: row for row in decisions.itertuples(index=False)}
    actionable = decisions[decisions["reason"] != "warmup"]
    evaluation_start = (
        pd.Timestamp(actionable.iloc[0]["decision_timestamp"])
        if not actionable.empty
        else pd.Timestamp(dates[-1])
    )

    cash = float(config.portfolio.initial_cash)
    units = {symbol: 0.0 for symbol in symbols}
    scenario = scenario_name(total_cost_bps, config.execution.base_total_cost_bps)
    fee_rate = config.execution.fee_bps / 10_000.0
    slippage_rate = (total_cost_bps - config.execution.fee_bps) / 10_000.0
    order_sequence = 0
    order_records: list[dict[str, Any]] = []
    equity_records: list[dict[str, Any]] = []

    def current_symbol() -> str | None:
        active = [symbol for symbol in symbols if units[symbol] > 1e-12]
        if len(active) > 1:
            raise RuntimeError("long-or-cash invariant violated")
        return active[0] if active else None

    def mark_equity(prices: pd.Series) -> float:
        return cash + sum(units[symbol] * float(prices[symbol]) for symbol in symbols)

    def sell(
        symbol: str,
        quantity: float,
        prices: pd.Series,
        decision: Any,
    ) -> None:
        nonlocal cash, order_sequence
        quantity = min(quantity, units[symbol])
        if quantity <= 1e-12:
            return
        reference_price = float(prices[symbol])
        execution_price = reference_price * (1.0 - slippage_rate)
        notional = quantity * execution_price
        fee = quantity * reference_price * fee_rate
        cash += notional - fee
        units[symbol] -= quantity
        if units[symbol] <= 1e-12:
            units[symbol] = 0.0
        order_sequence += 1
        order_records.append(
            _order_record(
                scenario=scenario,
                sequence=order_sequence,
                decision_time=decision.decision_timestamp,
                signal_as_of=decision.signal_as_of,
                symbol=symbol,
                side="SELL",
                quantity=quantity,
                reference_price=reference_price,
                execution_price=execution_price,
                fee=fee,
            )
        )

    def buy(
        symbol: str,
        desired_mid_notional: float,
        prices: pd.Series,
        decision: Any,
    ) -> None:
        nonlocal cash, order_sequence
        if desired_mid_notional <= 0.0:
            return
        reference_price = float(prices[symbol])
        execution_price = reference_price * (1.0 + slippage_rate)
        desired_quantity = desired_mid_notional / reference_price
        cash_per_unit = execution_price + reference_price * fee_rate
        quantity = min(desired_quantity, cash / cash_per_unit)
        if quantity <= 1e-12:
            return
        notional = quantity * execution_price
        fee = quantity * reference_price * fee_rate
        cash -= notional + fee
        if abs(cash) < 1e-8:
            cash = 0.0
        units[symbol] += quantity
        order_sequence += 1
        order_records.append(
            _order_record(
                scenario=scenario,
                sequence=order_sequence,
                decision_time=decision.decision_timestamp,
                signal_as_of=decision.signal_as_of,
                symbol=symbol,
                side="BUY",
                quantity=quantity,
                reference_price=reference_price,
                execution_price=execution_price,
                fee=fee,
            )
        )

    for timestamp in dates:
        open_prices = opens.loc[timestamp]
        decision = decision_map.get(timestamp)
        decision_reason: str | None = None
        decision_target: str | None = None
        decision_weight: float | None = None

        if decision is not None:
            decision_reason = str(decision.reason)
            decision_target = (
                str(decision.selected_symbol) if isinstance(decision.selected_symbol, str) else None
            )
            decision_weight = float(decision.target_weight)

            if decision.reason != "warmup":
                active = current_symbol()
                pretrade_equity = mark_equity(open_prices)
                target = decision_target
                target_weight = decision_weight

                if active is not None and active != target:
                    sell(active, units[active], open_prices, decision)
                    active = None

                if target is None:
                    if active is not None:
                        sell(active, units[active], open_prices, decision)
                elif active is None:
                    post_sale_equity = mark_equity(open_prices)
                    buy(
                        target,
                        post_sale_equity * target_weight,
                        open_prices,
                        decision,
                    )
                else:
                    current_value = units[target] * float(open_prices[target])
                    current_weight = current_value / pretrade_equity if pretrade_equity > 0 else 0.0
                    delta = target_weight - current_weight
                    if abs(delta) >= config.strategy.min_rebalance_delta:
                        target_value = target_weight * pretrade_equity
                        if delta < 0:
                            sell_quantity = (current_value - target_value) / float(
                                open_prices[target]
                            )
                            sell(target, sell_quantity, open_prices, decision)
                        else:
                            buy(
                                target,
                                target_value - current_value,
                                open_prices,
                                decision,
                            )

        close_prices = closes.loc[timestamp]
        equity = mark_equity(close_prices)
        exposure = sum(units[symbol] * float(close_prices[symbol]) for symbol in symbols)
        equity_records.append(
            {
                "scenario": scenario,
                "timestamp": timestamp,
                "equity": equity,
                "cash": cash,
                f"{symbols[0].lower()}_units": units[symbols[0]],
                f"{symbols[1].lower()}_units": units[symbols[1]],
                "gross_exposure": exposure / equity if equity > 0 else math.nan,
                "active_symbol": current_symbol(),
                "decision_reason": decision_reason,
                "decision_target": decision_target,
                "decision_weight": decision_weight,
            }
        )

    equity_frame = pd.DataFrame.from_records(equity_records)
    orders_frame = pd.DataFrame.from_records(
        order_records,
        columns=(
            "scenario",
            "order_id",
            "status",
            "decision_timestamp",
            "signal_as_of",
            "execution_timestamp",
            "symbol",
            "side",
            "quantity",
            "reference_price",
            "execution_price",
            "notional",
            "fee",
            "slippage_cost",
            "total_cost",
        ),
    )
    return SimulationResult(
        scenario=scenario,
        total_cost_bps=total_cost_bps,
        equity=equity_frame,
        orders=orders_frame,
        evaluation_start=evaluation_start,
    )


def build_paper_intents(decisions: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    sequence = 0
    for decision in decisions.itertuples(index=False):
        if decision.reason == "warmup":
            continue
        sequence += 1
        symbol = (
            decision.selected_symbol
            if isinstance(decision.selected_symbol, str)
            else config.universe.quote_asset
        )
        records.append(
            {
                "order_id": (
                    f"paper-{decision.decision_timestamp.strftime('%Y%m%d')}-{sequence:04d}"
                ),
                "status": "INTENT_ONLY",
                "decision_timestamp": decision.decision_timestamp,
                "signal_as_of": decision.signal_as_of,
                "intended_execution_timestamp": decision.decision_timestamp,
                "intent_type": "TARGET_ALLOCATION",
                "symbol": symbol,
                "target_weight": float(decision.target_weight),
                "reason": decision.reason,
                "network_used": False,
                "fill_assumed": False,
            }
        )
    return pd.DataFrame.from_records(
        records,
        columns=(
            "order_id",
            "status",
            "decision_timestamp",
            "signal_as_of",
            "intended_execution_timestamp",
            "intent_type",
            "symbol",
            "target_weight",
            "reason",
            "network_used",
            "fill_assumed",
        ),
    )
