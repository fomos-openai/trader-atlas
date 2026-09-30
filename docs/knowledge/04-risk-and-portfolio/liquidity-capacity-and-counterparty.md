---
id: liquidity-counterparty
title: 流动性、容量与对手方风险
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - risk-budget-sizing
related:
  - drawdown-stress-tail-and-regime-risk.md
  - ../02-markets-and-strategies/transaction-costs-liquidity-and-execution.md
sources:
  - https://www.iosco.org/library/pubdocs/pdf/IOSCOPD734.pdf
  - https://www.bis.org/publications/fsi-paper-27-cryptoasset-service-providers-financial-intermediaries-risks-and-policy-approaches
  - https://www.sfc.hk/en/Welcome-to-the-Fintech-Contact-Point/Virtual-assets/Virtual-asset-trading-platforms-operators/Lists-of-virtual-asset-trading-platforms
---

# 流动性、容量与对手方风险

市场方向判断正确也可能因无法成交、无法提款或平台故障而亏损。把这些风险单独预算，不能用历史价格波动率代替。

## 流动性

日线策略仍需限制订单相对正常与压力期成交量/盘口深度的比例。只有 OHLCV 时，容量结论应标记为低可信，并以更高滑点和部分无法成交压力测试。周末、重大事件和平台维护时段要单独观察。

容量不是固定金额。随着规模上升，冲击、完成时间、单一平台集中和资产转移风险可能非线性增加。对若干假设规模重算成本，取仍满足风险预算与流动性限制的保守上限。

## 平台与托管

记录平台法律实体、香港牌照核验日期、客户资产隔离、托管方、提款网络与限额、争议法域、历史中断和替代方案。SFC 名单是状态核验入口；持牌、证明储备或品牌规模都不是本金保证。

## 对手方上限

单一平台暴露上限应低于个人可永久失去的金额，并包含在途资产和平台内现金/稳定币。不同账户若属于同一法律实体或托管链，不算分散。任何“earn”、借贷、质押或双币安排都可能把单纯托管变成信用和流动性暴露，首版不使用。

## 事件触发器

提款延迟、条款变化、牌照状态变化、异常价差、账户限制、托管披露变化或平台无法对账时暂停新增意向，保存证据并重新尽调。不要等待价格损失后才把平台问题认定为风险事件。
