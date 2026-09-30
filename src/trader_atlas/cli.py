from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from trader_atlas.artifacts import RunArtifacts, deterministic_trial_id
from trader_atlas.config import AppConfig, load_config
from trader_atlas.data import ValidationReport, load_and_validate
from trader_atlas.engine import build_paper_intents, simulate
from trader_atlas.errors import TraderAtlasError
from trader_atlas.metrics import benchmark_metrics, simulation_metrics
from trader_atlas.strategy import compute_decisions

DEFAULT_CONFIG = "configs/btc-eth-spot-trend.yml"
DEFAULT_OUTPUT_ROOT = "artifacts/runs"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trader-atlas",
        description="Offline BTC/ETH trend-rotation research CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("validate-data", "Validate a local daily CSV or Parquet dataset."),
        ("research", "Run deterministic cost-stressed historical research."),
        ("paper", "Write offline target-allocation intentions; never place orders."),
    ):
        command = subparsers.add_parser(name, help=help_text)
        data_group = command.add_mutually_exclusive_group(required=True)
        data_group.add_argument(
            "--data",
            dest="data",
            help="Local .csv/.parquet/.pq market-data file",
        )
        data_group.add_argument(
            "--input",
            dest="data",
            help=argparse.SUPPRESS,
        )
        command.add_argument(
            "--config",
            default=DEFAULT_CONFIG,
            help="YAML config path (TOML is also accepted)",
        )
        command.add_argument(
            "--output-root",
            default=DEFAULT_OUTPUT_ROOT,
            help="Parent directory for immutable run folders",
        )
        command.add_argument(
            "--run-id",
            help="Optional deterministic run folder name (fails if it already exists)",
        )
    return parser


def _create_run(
    args: argparse.Namespace,
    config: AppConfig,
    config_bytes: bytes,
    report: ValidationReport,
) -> RunArtifacts:
    return RunArtifacts.create(
        output_root=args.output_root,
        command=args.command,
        run_id=args.run_id,
        config=config,
        config_path=args.config,
        config_bytes=config_bytes,
        input_path=args.data,
        input_sha256=report.sha256,
    )


def _validate_command(args: argparse.Namespace) -> Path:
    config, config_bytes = load_config(args.config)
    _, report = load_and_validate(args.data, config)
    run = _create_run(args, config, config_bytes, report)
    run.audit("data_validated", report.as_dict())
    run.write_json("validation.json", report.as_dict())
    run.write_json("metrics.json", {"mode": "validation_only"})
    run.write_frame("equity.csv", pd.DataFrame(columns=("timestamp", "equity")))
    run.write_frame("orders.csv", pd.DataFrame(columns=("order_id", "status")))
    trial = {
        "trial_id": deterministic_trial_id(
            report.sha256, config.as_dict(), "validate-data", "contract"
        ),
        "mode": "validate-data",
        "scenario": "contract",
        "status": "VALID",
        "validation": report.as_dict(),
    }
    run.write_jsonl("trial_ledger.jsonl", [trial])
    run.finalize(
        {
            "data": report.as_dict(),
            "summary": {"status": "VALID", "row_count": report.row_count},
        }
    )
    return run.run_dir


def _research_command(args: argparse.Namespace) -> Path:
    config, config_bytes = load_config(args.config)
    frame, report = load_and_validate(args.data, config)
    decisions = compute_decisions(frame, config)
    run = _create_run(args, config, config_bytes, report)
    run.audit("data_validated", report.as_dict())
    run.audit(
        "signals_computed",
        {
            "decision_count": int(len(decisions)),
            "actionable_decision_count": int((decisions["reason"] != "warmup").sum()),
        },
    )
    run.write_json("validation.json", report.as_dict())
    run.write_frame("decisions.csv", decisions)

    results = [
        simulate(frame, decisions, config, total_cost_bps)
        for total_cost_bps in config.execution.cost_scenarios_bps
    ]
    scenario_metrics = {result.scenario: simulation_metrics(result, config) for result in results}
    base = next(
        result
        for result in results
        if math.isclose(
            result.total_cost_bps,
            config.execution.base_total_cost_bps,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
    )
    metrics = {
        "mode": "research",
        "strategy": scenario_metrics,
        "benchmarks": benchmark_metrics(frame, config, base.evaluation_start),
    }
    equity = pd.concat([result.equity for result in results], ignore_index=True)
    orders = pd.concat([result.orders for result in results], ignore_index=True)
    trials = [
        {
            "trial_id": deterministic_trial_id(
                report.sha256, config.as_dict(), "research", result.scenario
            ),
            "mode": "research",
            "scenario": result.scenario,
            "status": "COMPLETE",
            "parameters": {
                "total_cost_bps": result.total_cost_bps,
                "fee_bps": config.execution.fee_bps,
                "slippage_bps": result.total_cost_bps - config.execution.fee_bps,
            },
            "metrics": scenario_metrics[result.scenario],
        }
        for result in results
    ]
    run.write_json("metrics.json", metrics)
    run.write_frame("equity.csv", equity)
    run.write_frame("orders.csv", orders)
    run.write_jsonl("trial_ledger.jsonl", trials)
    run.audit(
        "simulation_completed",
        {
            "scenarios": [result.scenario for result in results],
            "base_order_count": int(len(base.orders)),
        },
    )
    run.finalize(
        {
            "data": report.as_dict(),
            "summary": {
                "status": "COMPLETE",
                "scenario_count": len(results),
                "base_order_count": int(len(base.orders)),
            },
        }
    )
    return run.run_dir


def _paper_command(args: argparse.Namespace) -> Path:
    config, config_bytes = load_config(args.config)
    frame, report = load_and_validate(args.data, config)
    decisions = compute_decisions(frame, config)
    intents = build_paper_intents(decisions, config)
    run = _create_run(args, config, config_bytes, report)
    run.audit("data_validated", report.as_dict())
    run.audit(
        "paper_intentions_created",
        {
            "intent_count": int(len(intents)),
            "network_used": False,
            "fills_assumed": False,
        },
    )
    metrics = {
        "mode": "paper_intent_only",
        "intent_count": int(len(intents)),
        "risk_asset_intent_count": int(intents["symbol"].isin(config.universe.symbols).sum()),
        "network_used": False,
        "fills_assumed": False,
    }
    run.write_json("validation.json", report.as_dict())
    run.write_frame("decisions.csv", decisions)
    run.write_json("metrics.json", metrics)
    run.write_frame("equity.csv", pd.DataFrame(columns=("timestamp", "equity")))
    run.write_frame("orders.csv", intents)
    run.write_jsonl(
        "trial_ledger.jsonl",
        [
            {
                "trial_id": deterministic_trial_id(
                    report.sha256, config.as_dict(), "paper", "intent_only"
                ),
                "mode": "paper",
                "scenario": "intent_only",
                "status": "COMPLETE",
                "metrics": metrics,
            }
        ],
    )
    run.finalize(
        {
            "data": report.as_dict(),
            "summary": {
                "status": "COMPLETE",
                "intent_count": int(len(intents)),
                "network_used": False,
            },
        }
    )
    return run.run_dir


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate-data":
            run_dir = _validate_command(args)
        elif args.command == "research":
            run_dir = _research_command(args)
        elif args.command == "paper":
            run_dir = _paper_command(args)
        else:  # pragma: no cover - argparse enforces this
            raise AssertionError(f"unknown command: {args.command}")
    except (TraderAtlasError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"run_dir": str(run_dir.resolve())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
