---
id: data-contract-quality
title: 数据契约、质量与血缘
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - hypotheses-trial-ledger
related:
  - backtest-biases-and-cost-models.md
  - ../02-markets-and-strategies/crypto-spot-market-structure.md
sources:
  - https://pandas.pydata.org/docs/user_guide/timeseries.html
  - https://www.iosco.org/library/pubdocs/pdf/IOSCOPD734.pdf
---

# 数据契约、质量与血缘

## 数据契约

每个数据集都应声明：来源与许可、下载时间、资产/交易对、venue、报价货币、频率、时区、bar 定义、字段类型、缺失与修正规则、覆盖区间、哈希，以及“该字段在决策时何时可见”。未经契约的数据不得进入确认性回测。

数据血缘（lineage）从原始文件指向验证报告、清洗版本、特征和 run manifest。每个转换保存输入/输出哈希与代码版本；原始输入只读，派生数据应可重建。

## 质量检查

- 主键 `(venue, symbol, timestamp)` 唯一且严格递增；
- OHLC 关系有效，价格为正，成交量非负；
- 缺口、重复、异常跳点与零成交量被显式标记；
- BTC 与 ETH 日线采用相同 UTC 边界；
- 不静默 forward-fill 价格或成交量；
- 原始数据不可原地修改，清洗规则有版本。

异常不一定是错误：闪崩、停牌式中断或价差扩大可能正是风险事件。处理时同时保留原始值、质量标记和派生值，并在压力测试中重放。

## 特征可用性

移动均线和动量只能使用截至 `t` 的数据，并通过 `shift` 确保 `t` 日信号不在同一收盘价成交。窗口不足时输出 `NA`，不要自动缩短窗口。跨资产排序前先对齐可用时间，避免用 ETH 已收盘数据与 BTC 尚未完成的 bar 比较。

## 资产范围

首版资产范围固定为 BTC、ETH 和现金，避免 survivorship bias 与历史成分变化。扩展长尾币时必须保存每个时点真实可交易 universe、上市/下架、流动性和平台可用性，不能用今天的资产列表回看过去。
