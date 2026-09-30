#!/usr/bin/env python3
"""Repository acceptance checks for docs, simulation, and release artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

FRONT_MATTER_KEYS = {
    "id",
    "title",
    "status",
    "last_reviewed",
    "prerequisites",
    "related",
    "sources",
}
HK_FRONT_MATTER_KEYS = {"jurisdiction", "as_of", "review_due"}
ALLOWED_STATUSES = {"draft", "reviewed", "verified", "rejected"}

REQUIRED_DOCS = {
    "index.md",
    "paths/index.md",
    "paths/01-fast-track.md",
    "paths/02-stage-gates.md",
    "paths/03-roadmap-90-180-365.md",
    "knowledge/index.md",
    "knowledge/01-opc-operating-model/index.md",
    "knowledge/01-opc-operating-model/career-transition-and-edge.md",
    "knowledge/01-opc-operating-model/capital-runway-and-trading-policy.md",
    "knowledge/01-opc-operating-model/decision-journal-and-review.md",
    "knowledge/01-opc-operating-model/hong-kong-regulatory-and-tax-boundaries.md",
    "knowledge/02-markets-and-strategies/index.md",
    "knowledge/02-markets-and-strategies/crypto-spot-market-structure.md",
    "knowledge/02-markets-and-strategies/custody-counterparty-and-stablecoin-risk.md",
    "knowledge/02-markets-and-strategies/transaction-costs-liquidity-and-execution.md",
    "knowledge/02-markets-and-strategies/instruments-derivatives-and-dual-investment.md",
    "knowledge/02-markets-and-strategies/strategy-families-and-selection.md",
    "knowledge/02-markets-and-strategies/traditional-market-expansion.md",
    "knowledge/03-data-and-research/index.md",
    "knowledge/03-data-and-research/statistics-and-time-series.md",
    "knowledge/03-data-and-research/hypotheses-and-trial-ledger.md",
    "knowledge/03-data-and-research/data-contract-quality-and-lineage.md",
    "knowledge/03-data-and-research/backtest-biases-and-cost-models.md",
    "knowledge/03-data-and-research/out-of-sample-and-robustness.md",
    "knowledge/03-data-and-research/performance-measurement-and-attribution.md",
    "knowledge/04-risk-and-portfolio/index.md",
    "knowledge/04-risk-and-portfolio/risk-appetite-budget-and-sizing.md",
    "knowledge/04-risk-and-portfolio/portfolio-and-volatility-targeting.md",
    "knowledge/04-risk-and-portfolio/drawdown-stress-tail-and-regime-risk.md",
    "knowledge/04-risk-and-portfolio/liquidity-capacity-and-counterparty.md",
    "knowledge/04-risk-and-portfolio/guardrails-kill-switches-and-retirement.md",
    "knowledge/05-engineering-and-tools/index.md",
    "knowledge/05-engineering-and-tools/stack-selection.md",
    "knowledge/05-engineering-and-tools/research-data-and-reporting-pipeline.md",
    "knowledge/05-engineering-and-tools/paper-ledger-and-order-state.md",
    "knowledge/05-engineering-and-tools/testing-reproducibility-and-observability.md",
    "knowledge/05-engineering-and-tools/security-backup-and-disaster-recovery.md",
    "knowledge/06-production-discipline/index.md",
    "knowledge/06-production-discipline/research-to-paper-stage-gates.md",
    "knowledge/06-production-discipline/monitoring-drift-and-attribution.md",
    "knowledge/06-production-discipline/incident-change-and-model-risk.md",
    "knowledge/06-production-discipline/operating-review-routines.md",
    "knowledge/06-production-discipline/scale-pause-rework-or-retire.md",
    "knowledge/06-production-discipline/competency-and-readiness-scorecards.md",
    "practice/index.md",
    "practice/playbooks/choose-market-and-strategy.md",
    "practice/playbooks/validate-a-backtest.md",
    "practice/playbooks/start-pause-or-retire-paper-strategy.md",
    "practice/playbooks/handle-drawdown-data-or-venue-incident.md",
    "practice/playbooks/quarterly-strategy-review.md",
    "practice/templates/personal-trading-policy.md",
    "practice/templates/research-brief.md",
    "practice/templates/strategy-and-risk-card.md",
    "practice/templates/data-contract.md",
    "practice/templates/backtest-review.md",
    "practice/templates/risk-budget.md",
    "practice/templates/paper-runbook.md",
    "practice/templates/incident-postmortem.md",
    "practice/templates/trading-review.md",
    "case/btc-eth-spot-trend/index.md",
    "case/btc-eth-spot-trend/thesis.md",
    "case/btc-eth-spot-trend/data-contract.md",
    "case/btc-eth-spot-trend/backtest-protocol.md",
    "case/btc-eth-spot-trend/risk-spec.md",
    "case/btc-eth-spot-trend/paper-protocol.md",
    "case/btc-eth-spot-trend/results-interpretation.md",
    "references/index.md",
    "references/glossary.md",
    "references/official-sources.md",
    "references/bibliography.md",
    "references/tools-and-data.md",
}

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


class ValidationFailure(RuntimeError):
    """Raised when an acceptance check fails."""


def _fail(errors: list[str]) -> None:
    if errors:
        joined = "\n".join(f"- {item}" for item in errors)
        raise ValidationFailure(f"validation failed:\n{joined}")


def _front_matter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValidationFailure(f"{path.relative_to(ROOT)}: missing YAML front matter")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise ValidationFailure(f"{path.relative_to(ROOT)}: malformed YAML front matter")
    metadata = yaml.safe_load(parts[1])
    if not isinstance(metadata, dict):
        raise ValidationFailure(f"{path.relative_to(ROOT)}: front matter is not a mapping")
    return metadata, parts[2]


def _nav_paths(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        if value.endswith(".md"):
            yield value
        return
    if isinstance(value, list):
        for item in value:
            yield from _nav_paths(item)
        return
    if isinstance(value, dict):
        for item in value.values():
            yield from _nav_paths(item)


def _resolve_doc_link(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().strip("<>").split(maxsplit=1)[0]
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or target.startswith(("mailto:", "#")):
        return None
    path_text = unquote(parts.path)
    if not path_text:
        return None
    if path_text.startswith("/"):
        return None
    candidate = (source.parent / path_text).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return candidate
    if candidate.is_dir():
        candidate = candidate / "index.md"
    return candidate


def validate_docs() -> None:
    errors: list[str] = []
    actual = {path.relative_to(DOCS).as_posix() for path in DOCS.rglob("*.md")}
    for missing in sorted(REQUIRED_DOCS - actual):
        errors.append(f"missing approved documentation path: docs/{missing}")

    seen_ids: dict[str, Path] = {}
    for path in sorted(DOCS.rglob("*.md")):
        try:
            metadata, body = _front_matter(path)
        except ValidationFailure as exc:
            errors.append(str(exc))
            continue
        relative = path.relative_to(ROOT).as_posix()
        missing_keys = FRONT_MATTER_KEYS - metadata.keys()
        if missing_keys:
            errors.append(f"{relative}: missing front matter keys {sorted(missing_keys)}")
        if metadata.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{relative}: unsupported status {metadata.get('status')!r}")
        for name in ("prerequisites", "related", "sources"):
            if name in metadata and not isinstance(metadata[name], list):
                errors.append(f"{relative}: {name} must be a list")
        page_id = metadata.get("id")
        if not isinstance(page_id, str) or not page_id.strip():
            errors.append(f"{relative}: id must be a non-empty string")
        elif page_id in seen_ids:
            errors.append(
                f"{relative}: duplicate id {page_id!r} also used by "
                f"{seen_ids[page_id].relative_to(ROOT)}"
            )
        else:
            seen_ids[page_id] = path
        if "hong-kong-regulatory" in path.name:
            missing_hk = HK_FRONT_MATTER_KEYS - metadata.keys()
            if missing_hk:
                errors.append(f"{relative}: missing jurisdiction keys {sorted(missing_hk)}")
            if metadata.get("jurisdiction") not in {"HK", "Hong Kong"}:
                errors.append(f"{relative}: jurisdiction must identify Hong Kong")
        if not body.lstrip().startswith("# "):
            errors.append(f"{relative}: body must start with one H1 heading")

        for match in MARKDOWN_LINK_RE.finditer(body):
            candidate = _resolve_doc_link(path, match.group(1))
            if candidate is not None and not candidate.exists():
                display_target = (
                    candidate.relative_to(ROOT) if candidate.is_relative_to(ROOT) else candidate
                )
                errors.append(f"{relative}: broken link {match.group(1)!r} -> {display_target}")

    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    nav = set(_nav_paths(config.get("nav", [])))
    missing_from_nav = actual - nav
    if missing_from_nav:
        errors.append(f"docs not present in mkdocs nav: {sorted(missing_from_nav)}")
    bad_nav = nav - actual
    if bad_nav:
        errors.append(f"mkdocs nav points to missing docs: {sorted(bad_nav)}")

    registry_path = DOCS / "references/link-registry.yml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    links = registry.get("links")
    if not isinstance(links, dict):
        errors.append("docs/references/link-registry.yml: top-level links must be a mapping")
    else:
        for link_id, entry in links.items():
            if not isinstance(entry, dict) or not {"title", "path"} <= entry.keys():
                errors.append(f"link registry entry {link_id!r} needs title and path")
                continue
            target = ROOT / str(entry["path"])
            if not target.is_file():
                errors.append(f"link registry entry {link_id!r} points to missing {target}")

    _fail(errors)
    print(f"docs: OK ({len(actual)} Markdown pages, {len(seen_ids)} unique ids)")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_simulation() -> None:
    from trader_atlas.cli import main as cli_main

    data = ROOT / "tests/fixtures/btc-eth-daily-synthetic.csv"
    config = ROOT / "configs/btc-eth-spot-trend.yml"
    errors: list[str] = []
    if not data.is_file():
        errors.append(f"missing deterministic fixture: {data.relative_to(ROOT)}")
    if not config.is_file():
        errors.append(f"missing approved config: {config.relative_to(ROOT)}")
    _fail(errors)

    with tempfile.TemporaryDirectory(prefix="trader-atlas-validation-") as directory:
        output = Path(directory) / "runs"
        for run_id in ("deterministic-a", "deterministic-b"):
            result = cli_main(
                [
                    "research",
                    "--config",
                    str(config),
                    "--data",
                    str(data),
                    "--output-root",
                    str(output),
                    "--run-id",
                    run_id,
                ]
            )
            if result != 0:
                errors.append(f"research command failed for {run_id} with exit code {result}")
        _fail(errors)

        first = output / "deterministic-a"
        second = output / "deterministic-b"
        deterministic_files = {
            "validation.json",
            "metrics.json",
            "decisions.csv",
            "equity.csv",
            "orders.csv",
            "trial_ledger.jsonl",
        }
        for relative in sorted(deterministic_files):
            left = first / relative
            right = second / relative
            if not left.is_file() or not right.is_file():
                errors.append(f"missing deterministic artifact: {relative}")
            elif left.read_bytes() != right.read_bytes():
                errors.append(f"double-run mismatch: {relative}")

        metrics = json.loads((first / "metrics.json").read_text(encoding="utf-8"))
        strategy = metrics.get("strategy", {})
        scenarios = list(strategy)
        if len(scenarios) < 3:
            errors.append("metrics must contain the base, 25 bp, and 40 bp cost scenarios")
        final_equities = [strategy[name].get("final_equity") for name in scenarios]
        if any(value is None for value in final_equities):
            errors.append("every strategy cost scenario must report final_equity")
        elif any(
            later > earlier + 1e-10
            for earlier, later in zip(final_equities, final_equities[1:], strict=False)
        ):
            errors.append("higher transaction costs increased final equity")

        orders_text = (first / "orders.csv").read_text(encoding="utf-8")
        if "SIMULATED_FILL" not in orders_text:
            errors.append("research orders do not contain simulated fills")

        paper_result = cli_main(
            [
                "paper",
                "--config",
                str(config),
                "--data",
                str(data),
                "--output-root",
                str(output),
                "--run-id",
                "paper-intent",
            ]
        )
        if paper_result != 0:
            errors.append(f"paper command failed with exit code {paper_result}")
        else:
            paper_metrics = json.loads(
                (output / "paper-intent/metrics.json").read_text(encoding="utf-8")
            )
            if paper_metrics.get("network_used") is not False:
                errors.append("paper mode did not assert network_used=false")
            if paper_metrics.get("fills_assumed") is not False:
                errors.append("paper mode did not assert fills_assumed=false")

    _fail(errors)
    print("simulation: OK (deterministic double-run, cost stress, paper intent)")


def _find_delivery_results(payload: Any) -> tuple[bool, bool]:
    text = json.dumps(payload, ensure_ascii=False).lower()
    passing_tokens = ('"passed"', '"pass"', '"ok"')
    strict_ok = "strict" in text and any(token in text for token in passing_tokens)
    browser_ok = "browser" in text and any(token in text for token in passing_tokens)
    return strict_ok, browser_ok


def validate_artifacts() -> None:
    from pypdf import PdfReader

    errors: list[str] = []
    html = ROOT / "00-knowledge-map.html"
    delivery = ROOT / "00-knowledge-map.delivery.json"
    preview = ROOT / "docs/assets/knowledge-map-preview.png"
    pdf = ROOT / "output/pdf/trader-atlas.pdf"
    for path in (html, delivery, preview, pdf):
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty release artifact: {path.relative_to(ROOT)}")
    _fail(errors)

    html_text = html.read_text(encoding="utf-8", errors="replace")
    for phrase in ("Trader Atlas", "zh-CN", "BTC/ETH"):
        if phrase not in html_text:
            errors.append(f"knowledge map does not contain required phrase {phrase!r}")
    try:
        payload = json.loads(delivery.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid delivery sidecar JSON: {exc}")
    else:
        strict_ok, browser_ok = _find_delivery_results(payload)
        if not strict_ok:
            errors.append("delivery sidecar does not record a passing strict check")
        if not browser_ok:
            errors.append("delivery sidecar does not record a passing browser check")

    reader = PdfReader(str(pdf))
    if not 45 <= len(reader.pages) <= 70:
        errors.append(f"PDF page count must be 45-70, got {len(reader.pages)}")
    metadata: Any = reader.metadata or {}
    if "Trader Atlas" not in str(metadata.get("/Title", "")):
        errors.append("PDF title metadata is missing Trader Atlas")
    if not reader.outline:
        errors.append("PDF has no outline/bookmarks")
    link_count = 0
    embedded_font_count = 0
    for page in reader.pages:
        for annotation in page.get("/Annots", []):
            obj = annotation.get_object()
            if obj.get("/Subtype") == "/Link":
                link_count += 1
        resources = page.get("/Resources")
        if not resources:
            continue
        fonts = resources.get("/Font")
        if not fonts:
            continue
        for ref in fonts.values():
            font = ref.get_object()
            descriptor = font.get("/FontDescriptor")
            if descriptor:
                descriptor = descriptor.get_object()
                if any(descriptor.get(key) for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                    embedded_font_count += 1
    if link_count == 0:
        errors.append("PDF contains no clickable links")
    if embedded_font_count == 0:
        errors.append("PDF contains no embedded font program")

    packaged_map = ROOT / "site/knowledge-map/index.html"
    if packaged_map.exists() and _sha256(packaged_map) != _sha256(html):
        errors.append("Pages knowledge-map copy differs from root HTML")
    packaged_pdf = ROOT / "site/downloads/trader-atlas.pdf"
    if packaged_pdf.exists() and _sha256(packaged_pdf) != _sha256(pdf):
        errors.append("Pages PDF copy differs from release PDF")

    _fail(errors)
    print(
        f"artifacts: OK ({len(reader.pages)} PDF pages, {link_count} links, "
        f"map sha256={_sha256(html)[:12]})"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("docs", "simulation", "artifacts"))
    args = parser.parse_args()
    try:
        if args.mode == "docs":
            validate_docs()
        elif args.mode == "simulation":
            validate_simulation()
        else:
            validate_artifacts()
    except ValidationFailure as exc:
        print(exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
