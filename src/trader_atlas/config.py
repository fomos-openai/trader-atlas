from __future__ import annotations

import math
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from trader_atlas.errors import ConfigurationError


@dataclass(frozen=True)
class UniverseConfig:
    symbols: tuple[str, str]
    quote_asset: str


@dataclass(frozen=True)
class StrategyConfig:
    momentum_days: int
    sma_days: int
    volatility_days: int
    target_annual_volatility: float
    annualization_days: int
    max_weight: float
    min_rebalance_delta: float
    rebalance_weekday: int


@dataclass(frozen=True)
class ExecutionConfig:
    fee_bps: float
    slippage_bps: float
    cost_scenarios_bps: tuple[float, ...]
    fill_method: str

    @property
    def base_total_cost_bps(self) -> float:
        return self.fee_bps + self.slippage_bps


@dataclass(frozen=True)
class PortfolioConfig:
    initial_cash: float


@dataclass(frozen=True)
class DataConfig:
    timestamp_column: str
    symbol_column: str
    timestamp_semantics: str
    require_daily_continuity: bool


@dataclass(frozen=True)
class PaperConfig:
    intent_only: bool


@dataclass(frozen=True)
class AppConfig:
    universe: UniverseConfig
    strategy: StrategyConfig
    execution: ExecutionConfig
    portfolio: PortfolioConfig
    data: DataConfig
    paper: PaperConfig

    @property
    def warmup_bars(self) -> int:
        return max(
            self.strategy.sma_days,
            self.strategy.momentum_days + 1,
            self.strategy.volatility_days + 1,
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _section(raw: dict[str, Any], name: str) -> dict[str, Any]:
    value = raw.get(name)
    if not isinstance(value, dict):
        raise ConfigurationError(f"missing [{name}] configuration section")
    return value


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigurationError(f"{name} must be a positive integer")
    return value


def _integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigurationError(f"{name} must be an integer")
    return value


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ConfigurationError(f"{name} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{name} must be numeric") from exc


def _fraction(value: Any, name: str, *, allow_one: bool = False) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{name} must be numeric") from exc
    upper_ok = parsed <= 1.0 if allow_one else parsed < 1.0
    if parsed <= 0.0 or not upper_ok:
        bound = "(0, 1]" if allow_one else "(0, 1)"
        raise ConfigurationError(f"{name} must be in {bound}")
    return parsed


def load_config(path: str | Path) -> tuple[AppConfig, bytes]:
    config_path = Path(path)
    try:
        payload = config_path.read_bytes()
    except OSError as exc:
        raise ConfigurationError(f"cannot read config: {config_path}") from exc

    suffix = config_path.suffix.lower()
    try:
        text = payload.decode("utf-8")
        if suffix in {".yml", ".yaml"}:
            raw = yaml.safe_load(text)
        elif suffix == ".toml":
            raw = tomllib.loads(text)
        else:
            raise ConfigurationError("config must be a .yml, .yaml, or .toml file")
    except ConfigurationError:
        raise
    except (UnicodeDecodeError, tomllib.TOMLDecodeError, yaml.YAMLError) as exc:
        label = "YAML" if suffix in {".yml", ".yaml"} else "TOML"
        raise ConfigurationError(f"invalid {label} config: {config_path}") from exc
    if not isinstance(raw, dict):
        raise ConfigurationError("config root must be a mapping")

    universe = _section(raw, "universe")
    strategy = _section(raw, "strategy")
    execution = _section(raw, "execution")
    portfolio = _section(raw, "portfolio")
    data = _section(raw, "data")
    paper = _section(raw, "paper")

    symbols_raw = universe.get("symbols")
    if not isinstance(symbols_raw, list) or len(symbols_raw) != 2:
        raise ConfigurationError("universe.symbols must contain exactly two symbols")
    symbols = tuple(str(item).strip().upper() for item in symbols_raw)
    if any(not item for item in symbols) or len(set(symbols)) != 2:
        raise ConfigurationError("universe.symbols must be two distinct non-empty symbols")

    cost_scenarios_raw = execution.get("cost_scenarios_bps")
    if not isinstance(cost_scenarios_raw, list) or not cost_scenarios_raw:
        raise ConfigurationError("execution.cost_scenarios_bps must be a non-empty array")
    cost_scenarios_bps = tuple(float(item) for item in cost_scenarios_raw)
    if any(not math.isfinite(item) or item <= 0 for item in cost_scenarios_bps):
        raise ConfigurationError("cost scenarios must be finite and positive")
    if len(set(cost_scenarios_bps)) != len(cost_scenarios_bps):
        raise ConfigurationError("cost scenarios must be unique")
    if cost_scenarios_bps != tuple(sorted(cost_scenarios_bps)):
        raise ConfigurationError("cost scenarios must be sorted from low to high")

    config = AppConfig(
        universe=UniverseConfig(
            symbols=(symbols[0], symbols[1]),
            quote_asset=str(universe.get("quote_asset", "")).strip().upper(),
        ),
        strategy=StrategyConfig(
            momentum_days=_positive_int(strategy.get("momentum_days"), "strategy.momentum_days"),
            sma_days=_positive_int(strategy.get("sma_days"), "strategy.sma_days"),
            volatility_days=_positive_int(
                strategy.get("volatility_days"), "strategy.volatility_days"
            ),
            target_annual_volatility=_fraction(
                strategy.get("target_annual_volatility"),
                "strategy.target_annual_volatility",
            ),
            annualization_days=_positive_int(
                strategy.get("annualization_days"), "strategy.annualization_days"
            ),
            max_weight=_fraction(strategy.get("max_weight"), "strategy.max_weight", allow_one=True),
            min_rebalance_delta=_fraction(
                strategy.get("min_rebalance_delta"),
                "strategy.min_rebalance_delta",
                allow_one=True,
            ),
            rebalance_weekday=_integer(
                strategy.get("rebalance_weekday"), "strategy.rebalance_weekday"
            ),
        ),
        execution=ExecutionConfig(
            fee_bps=_number(execution.get("fee_bps"), "execution.fee_bps"),
            slippage_bps=_number(execution.get("slippage_bps"), "execution.slippage_bps"),
            cost_scenarios_bps=cost_scenarios_bps,
            fill_method=str(execution.get("fill_method", "")).strip(),
        ),
        portfolio=PortfolioConfig(
            initial_cash=_number(portfolio.get("initial_cash"), "portfolio.initial_cash")
        ),
        data=DataConfig(
            timestamp_column=str(data.get("timestamp_column", "timestamp")),
            symbol_column=str(data.get("symbol_column", "symbol")),
            timestamp_semantics=str(data.get("timestamp_semantics", "")),
            require_daily_continuity=bool(data.get("require_daily_continuity", True)),
        ),
        paper=PaperConfig(intent_only=bool(paper.get("intent_only", True))),
    )
    _validate_config(config)
    return config, payload


def _validate_config(config: AppConfig) -> None:
    if not config.universe.quote_asset:
        raise ConfigurationError("universe.quote_asset must not be empty")
    if not 0 <= config.strategy.rebalance_weekday <= 6:
        raise ConfigurationError("strategy.rebalance_weekday must be between 0 and 6")
    if config.execution.fee_bps < 0 or config.execution.slippage_bps < 0:
        raise ConfigurationError("execution costs cannot be negative")
    base_cost = config.execution.base_total_cost_bps
    if not any(
        math.isclose(item, base_cost, rel_tol=0.0, abs_tol=1e-12)
        for item in config.execution.cost_scenarios_bps
    ):
        raise ConfigurationError("execution.cost_scenarios_bps must include fee_bps + slippage_bps")
    if any(item < config.execution.fee_bps for item in config.execution.cost_scenarios_bps):
        raise ConfigurationError("each total-cost scenario must be at least execution.fee_bps")
    if config.execution.fill_method != "next_bar_open":
        raise ConfigurationError("v0.1 only supports fill_method='next_bar_open'")
    if config.portfolio.initial_cash <= 0:
        raise ConfigurationError("portfolio.initial_cash must be positive")
    if config.data.timestamp_semantics != "bar_open_utc":
        raise ConfigurationError("v0.1 requires data.timestamp_semantics='bar_open_utc'")
    if not config.paper.intent_only:
        raise ConfigurationError("paper.intent_only must remain true in v0.1")
