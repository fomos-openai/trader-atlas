---
id: transaction-costs-liquidity-execution
title: 交易成本、流动性与执行
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - crypto-spot-market-structure
related:
  - ../04-risk-and-portfolio/liquidity-capacity-and-counterparty.md
  - ../../case/btc-eth-spot-trend/backtest-protocol.md
sources:
  - https://www.iosco.org/library/pubdocs/pdf/IOSCOPD734.pdf
  - https://www.bis.org/publ/bppdf/bispap138.pdf
---

# 交易成本、流动性与执行

保守单边成本至少包括 `fee + half-spread + market impact + latency drift + funding/transfer cost`。资产轮动有卖出与买入两腿，不能只扣一次费用。maker rebate 不应作为默认成交假设，因为排队与未成交也有成本。

用总单边成本 15/25/40 bps 情景检验安全边际，并报告成本占毛收益和换手。若只能获得 OHLCV，容量结论应标低可信；实际规模上限还需盘口深度、订单占正常/压力期成交量比例和部分成交模型。

案例固定用周一开盘模拟成交，信号只用此前完整日线。任何改为同一收盘成交、跳过缺失 bar 或静默使用下一可用价格的实现，都改变了执行假设，必须作为新版本审查。
