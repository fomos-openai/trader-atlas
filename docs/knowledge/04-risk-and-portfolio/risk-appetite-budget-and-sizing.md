---
id: risk-budget-sizing
title: 风险偏好、风险预算与仓位
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - knowledge-risk-portfolio-home
related:
  - guardrails-kill-switches-and-retirement.md
  - ../../practice/templates/strategy-and-risk-card.md
sources:
  - https://doi.org/10.1111/jofi.12513
  - https://www.bis.org/committees/bcbs/basel-framework/standard/sco?allChapters=true
---

# 风险偏好、风险预算与仓位

## 三个不同问题

- **风险承受能力（capacity）**：损失后生活与经营是否仍可持续。
- **风险意愿（tolerance）**：心理与行为上能否遵守规则。
- **风险预算（budget）**：预先分配给策略、资产与平台的量化上限。

取三者中最小值。不能因为回测收益高就提高 capacity。

## 仓位框架

首个案例 long/cash 且最大总敞口不超过 100%。可用固定权重作为最透明基准；若使用 volatility targeting，波动估计必须只使用过去数据、设置最小/最大缩放并承认波动在跳跃行情中滞后。任何公式都要受绝对仓位、资产集中和平台集中上限约束。

风险预算建议用政策变量表达，而非仓库硬编码个人数字：

- `max_strategy_drawdown`
- `max_asset_weight`
- `max_venue_exposure`
- `max_turnover_per_rebalance`
- `stale_data_limit`

数值由个人交易政策给出，配置变更需要新版本和重新回测。

## 评审问题

仓位翻倍时最坏损失是否也近似翻倍？流动性与平台风险是否非线性增加？若答案不清楚，先减小规模。风险预算应以“最坏仍能继续研究”为目标，而不是把回测允许的最大杠杆用满。
