---
id: research-data-reporting-pipeline
title: 研究、数据与报告流水线
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - stack-selection
related:
  - paper-ledger-and-order-state.md
  - testing-reproducibility-and-observability.md
  - ../03-data-and-research/backtest-biases-and-cost-models.md
sources:
  - https://pandas.pydata.org/docs/user_guide/timeseries.html
  - https://docs.pytest.org/en/stable/how-to/fixtures.html
---

# 研究、数据与报告流水线

## 单向数据流

`raw CSV → schema validation → canonical bars → features → lagged targets → simulated fills → ledger → metrics/report`

每一阶段写出明确对象，不允许后续模块悄悄修复上游数据。错误应携带 run ID、资产、时间戳和规则名，并使运行失败。

研究与本地 paper 共用 `signals`、成本模型、组合约束和输出 schema；paper 的状态与意向语义见[账本与订单状态](paper-ledger-and-order-state.md)。

## 输出契约

- `metrics.json`：净指标、风险、换手、样本标记与限制；
- `equity.csv`：每个时间点的现金、持仓价值、权益与回撤；
- `orders.csv`：意向、模拟成交、费用、状态和原因；
- `run-manifest.json`：版本、哈希、配置和输出文件摘要。

输出默认写入未跟踪的 `artifacts/`；要分享结论时，只提交经审查的摘要与 manifest，不提交敏感账户数据。
