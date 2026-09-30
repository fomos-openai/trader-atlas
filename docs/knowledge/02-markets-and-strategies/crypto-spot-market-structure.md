---
id: crypto-spot-market-structure
title: 数字资产现货市场结构
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - knowledge-markets-strategies-home
related:
  - custody-counterparty-and-stablecoin-risk.md
  - transaction-costs-liquidity-and-execution.md
sources:
  - https://www.iosco.org/library/pubdocs/pdf/IOSCOPD734.pdf
  - https://www.bis.org/publ/bppdf/bispap138.pdf
  - https://www.sfc.hk/en/News-and-announcements/Policy-statements-and-announcements/Statement-on-virtual-asset-arrangements-claiming-to-offer-returns-to-investors
---

# 数字资产现货市场结构

## 交易链条

研究价格通常来自某个具体 venue 的 order book 或 candle，而真实结果还经过下单、排队、成交、费用、资产记账和提款。BTC/ETH 的“市场价”不是单一真值；不同平台可能在时区、成交源、异常处理和报价货币上不同。

现货交易的资产交割与托管安排不同于衍生品保证金，但不等于无对手方风险。订单簿深度、报价货币、交易对法律实体和数据来源都要进入数据契约。

## 数据检查

- 使用 UTC 存储，明确 candle 的开闭区间；
- 检查重复、缺口、零成交量、极端跳点与交易对重命名；
- 保留原始下载时间、来源 URL/API、哈希和修正规则；
- 策略计算与 paper 使用同一 close 定义；
- 平台/报价货币变化必须触发数据版本升级。
