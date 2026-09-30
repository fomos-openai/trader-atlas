---
id: case-btc-eth
title: BTC/ETH 现货趋势轮动 Python 案例
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - strategy-selection
  - stack-selection
related:
  - thesis.md
  - data-contract.md
  - ../../paths/02-stage-gates.md
  - backtest-protocol.md
sources:
  - ../../../src/trader_atlas/strategy.py
  - ../../../src/trader_atlas/engine.py
  - ../../../configs/btc-eth-spot-trend.yml
  - ../../../data/README.md
---

# BTC/ETH 现货趋势轮动 Python 案例

这是研究流程样例，不是推荐策略。它把 BTC、ETH 与现金限制在 long/cash 组合，并用同一配置驱动数据验证、历史研究和本地 paper intentions。

## 冻结规则

- 输入：BTC、ETH 的连续 UTC 日线 OHLCV，本地 CSV 或 Parquet；不自动下载。
- 决策：每周一开盘前，仅使用周一之前已完成的 bar。
- 资格：最新 close 高于 200 日 SMA，且 90 日 momentum 为正。
- 选择：合格资产中选择 90 日 momentum 较高者，否则持现金。
- 仓位：用过去 30 日波动率缩放到 15% 年化目标，上限 99%；权重变化不足 5% 时不调仓。
- 成交：下一根 bar 的开盘价；基准单边成本为 10 bps fee + 5 bps slippage，并运行
  15/25/40 bps 总单边成本情景。

参数只是透明基准，没有被证明最优。任何改动都应创建新 trial 并重新审查。

## 准备数据

从仓库根目录执行。数据文件必须满足仓库
[`data/README.md`](https://github.com/fomos-openai/trader-atlas/blob/main/data/README.md)
中的契约：`timestamp,symbol,open,high,low,close,volume`，每日 `00:00:00Z`，BTC/ETH
日历一致，默认至少 201 个 warm-up bar 加一个可决策 bar。真实或受许可数据保留在 Git 之外。

建议按顺序阅读[研究假设](thesis.md)、[数据契约](data-contract.md)、[回测协议](backtest-protocol.md)、[风险规格](risk-spec.md)、[本地 Paper 协议](paper-protocol.md)和[结果解读](results-interpretation.md)，不要只运行命令后读取单个收益指标。

## 运行

```bash
uv sync --all-extras --all-groups

uv run trader-atlas validate-data \
  --data /absolute/path/btc_eth_daily.csv \
  --config configs/btc-eth-spot-trend.yml

uv run trader-atlas research \
  --data /absolute/path/btc_eth_daily.csv \
  --config configs/btc-eth-spot-trend.yml

uv run trader-atlas paper \
  --data /absolute/path/btc_eth_daily.csv \
  --config configs/btc-eth-spot-trend.yml
```

每次运行创建不可覆盖的 `artifacts/runs/<run-id>/`，包含配置快照、数据验证、decisions、metrics、equity、orders/intents、trial ledger、audit log、manifest 与 SHA-256。指定已存在的 `--run-id` 应失败，防止覆盖证据。

## 三种命令的语义

- `validate-data`：只验证数据契约，不评价策略。
- `research`：历史模拟并比较成本压力和现金/BTC/ETH/等权基准；输出的收益是特定数据与假设下的模拟。
- `paper`：只生成离线目标配置意向，`network_used=false`、`fills_assumed=false`；不维护真实账户，也不允许下单。

## 正确解读

先检查 manifest、验证报告和订单时间，再看绩效。`Sharpe` 使用零现金利率，仅供同口径比较；合成或测试数据的任何收益都没有投资含义。只有冻结规则通过样本外、成本、参数邻域与逐时 paper 审查，才能得到“值得继续研究”的结论，仍不能推导未来收益或实盘适用性。
