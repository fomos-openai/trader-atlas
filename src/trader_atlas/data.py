from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from trader_atlas.config import AppConfig
from trader_atlas.errors import DataContractError

MARKET_COLUMNS = ("timestamp", "symbol", "open", "high", "low", "close", "volume")


@dataclass(frozen=True)
class ValidationReport:
    path: str
    format: str
    sha256: str
    row_count: int
    rows_per_symbol: dict[str, int]
    start: str
    end: str
    timezone: str
    timestamp_semantics: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_market_data(path: str | Path, config: AppConfig) -> pd.DataFrame:
    source = Path(path)
    if not source.is_file():
        raise DataContractError(f"input file does not exist: {source}")

    suffix = source.suffix.lower()
    try:
        if suffix == ".csv":
            frame = pd.read_csv(source)
        elif suffix in {".parquet", ".pq"}:
            frame = pd.read_parquet(source)
        else:
            raise DataContractError("input must be a .csv, .parquet, or .pq file")
    except DataContractError:
        raise
    except ImportError as exc:
        raise DataContractError("Parquet input requires the declared pyarrow dependency") from exc
    except Exception as exc:
        raise DataContractError(f"could not read market data: {source}") from exc

    rename = {
        config.data.timestamp_column: "timestamp",
        config.data.symbol_column: "symbol",
    }
    frame = frame.rename(columns=rename)
    missing = [column for column in MARKET_COLUMNS if column not in frame.columns]
    if missing:
        raise DataContractError(f"missing required columns: {', '.join(missing)}")
    return frame.loc[:, MARKET_COLUMNS].copy()


def validate_market_data(
    frame: pd.DataFrame, source_path: str | Path, config: AppConfig
) -> tuple[pd.DataFrame, ValidationReport]:
    if frame.empty:
        raise DataContractError("market data is empty")

    normalized = frame.copy()
    normalized["timestamp"] = pd.to_datetime(normalized["timestamp"], utc=True, errors="coerce")
    if normalized["timestamp"].isna().any():
        raise DataContractError("timestamp contains invalid or missing values")
    not_midnight = (
        normalized["timestamp"].dt.hour.ne(0)
        | normalized["timestamp"].dt.minute.ne(0)
        | normalized["timestamp"].dt.second.ne(0)
        | normalized["timestamp"].dt.microsecond.ne(0)
        | normalized["timestamp"].dt.nanosecond.ne(0)
    )
    if bool(not_midnight.any()):
        raise DataContractError("daily timestamps must identify the 00:00 UTC bar open")

    normalized["symbol"] = normalized["symbol"].astype(str).str.strip().str.upper()
    for column in ("open", "high", "low", "close", "volume"):
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
        values = normalized[column].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise DataContractError(f"{column} contains non-finite or missing values")

    if normalized.duplicated(["symbol", "timestamp"]).any():
        raise DataContractError("duplicate symbol/timestamp rows are not allowed")
    if (normalized[["open", "high", "low", "close"]] <= 0).any(axis=None):
        raise DataContractError("OHLC prices must be strictly positive")
    if (normalized["volume"] < 0).any():
        raise DataContractError("volume cannot be negative")

    upper = normalized[["open", "close", "low"]].max(axis=1)
    lower = normalized[["open", "close", "high"]].min(axis=1)
    if (normalized["high"] < upper).any() or (normalized["low"] > lower).any():
        raise DataContractError("OHLC relationships are inconsistent")

    expected_symbols = set(config.universe.symbols)
    actual_symbols = set(normalized["symbol"])
    missing_symbols = sorted(expected_symbols - actual_symbols)
    if missing_symbols:
        raise DataContractError(f"missing configured symbols: {', '.join(missing_symbols)}")
    normalized = normalized[normalized["symbol"].isin(expected_symbols)].copy()
    normalized = normalized.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    calendars: dict[str, pd.DatetimeIndex] = {}
    rows_per_symbol: dict[str, int] = {}
    for symbol in config.universe.symbols:
        timestamps = pd.DatetimeIndex(normalized.loc[normalized["symbol"] == symbol, "timestamp"])
        rows_per_symbol[symbol] = len(timestamps)
        if len(timestamps) < config.warmup_bars + 1:
            raise DataContractError(
                f"{symbol} requires at least {config.warmup_bars + 1} daily rows"
            )
        if not timestamps.is_monotonic_increasing:
            raise DataContractError(f"{symbol} timestamps are not increasing")
        if config.data.require_daily_continuity:
            gaps = timestamps.to_series().diff().dropna()
            one_day_nanoseconds = 86_400_000_000_000
            if not (gaps.array.asi8 == one_day_nanoseconds).all():
                raise DataContractError(f"{symbol} has missing or non-daily bars")
        calendars[symbol] = timestamps

    first_calendar = calendars[config.universe.symbols[0]]
    for symbol in config.universe.symbols[1:]:
        if not first_calendar.equals(calendars[symbol]):
            raise DataContractError("configured symbols must share the same daily calendar")

    source = Path(source_path)
    report = ValidationReport(
        path=str(source.resolve()),
        format=source.suffix.lower().lstrip("."),
        sha256=sha256_file(source),
        row_count=len(normalized),
        rows_per_symbol=rows_per_symbol,
        start=first_calendar.min().isoformat(),
        end=first_calendar.max().isoformat(),
        timezone="UTC",
        timestamp_semantics=config.data.timestamp_semantics,
    )
    return normalized, report


def load_and_validate(path: str | Path, config: AppConfig) -> tuple[pd.DataFrame, ValidationReport]:
    return validate_market_data(load_market_data(path, config), path, config)
