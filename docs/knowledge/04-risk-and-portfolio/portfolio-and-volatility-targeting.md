---
id: portfolio-volatility-targeting
title: 组合构建与波动率目标
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - risk-budget-sizing
related:
  - drawdown-stress-tail-and-regime-risk.md
  - ../02-markets-and-strategies/strategy-families-and-selection.md
sources:
  - https://doi.org/10.1111/jofi.12513
  - https://doi.org/10.1111/j.1540-6261.1952.tb01525.x
---

# 组合构建与波动率目标

组合按风险源而非资产数量描述。BTC 与 ETH 在压力期可能高度相关；轮动只持一个风险资产并不自动提供分散，现金才是首版主要降险工具。

案例用过去 30 日实现波动率估计，将目标仓位缩放到 15% 年化波动并封顶 99%。这是风险平滑机制，不是损失保证：估计有滞后，跳跃风险和相关性上升可能使实际风险显著超标。

实现时只用历史收益，处理零/非有限波动，并以绝对总敞口、资产和平台上限覆盖公式结果。报告平均/最大敞口、现金时段和目标与实际模拟波动的差异。固定权重版本应作为更简单基准，以验证缩放是否真正改善风险路径。
