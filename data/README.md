# Local market-data contract

The research CLI reads one local, long-form CSV or Parquet file. It never downloads
data. A valid file contains exactly one daily row per configured symbol and UTC day:

| column | meaning |
| --- | --- |
| `timestamp` | UTC daily bar open, exactly `00:00:00+00:00` |
| `symbol` | canonical base symbol (`BTC` or `ETH` in the default config) |
| `open`, `high`, `low`, `close` | positive quote-asset prices |
| `volume` | non-negative base-asset volume |

Example CSV rows:

```csv
timestamp,symbol,open,high,low,close,volume
2024-01-01T00:00:00Z,BTC,42000,42500,41500,42300,1234
2024-01-01T00:00:00Z,ETH,2280,2320,2240,2300,9876
```

Validation is intentionally strict:

- timestamps must be unique per symbol, continuous at one-day intervals, and use
  the same calendar for both symbols;
- OHLC values must be finite and internally consistent;
- each symbol needs at least 201 rows for the default 200-day warm-up;
- missing prices are never forward-filled;
- extra symbols are ignored after the configured BTC/ETH pair is verified.

The timestamp identifies the **bar open**. A Monday decision can use only rows before
Monday and is simulated at Monday's open. This convention makes the no-lookahead rule
machine-testable.

Parquet support uses the declared `pyarrow` dependency. CSV and Parquet represent the
same schema; neither format changes strategy behavior.

Validate a local file with the public `--data` interface and the reviewed YAML
baseline:

```bash
uv run trader-atlas validate-data \
  --config configs/btc-eth-spot-trend.yml \
  --data /absolute/path/btc_eth_daily.csv
```

`tests/fixtures/btc-eth-daily-synthetic.csv` is deterministic test material. It is
safe for implementation checks but has no market or performance meaning.

Keep licensed or private market data outside Git. Every run records the input file's
SHA-256 checksum in `artifacts/runs/<run-id>/manifest.json` so a result can be tied to
the exact local bytes without publishing the data itself.
