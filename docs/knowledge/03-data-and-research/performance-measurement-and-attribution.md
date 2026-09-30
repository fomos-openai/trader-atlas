---
id: performance-measurement-attribution
title: 绩效度量与归因
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - backtest-biases
related:
  - ../06-production-discipline/monitoring-drift-and-attribution.md
  - ../04-risk-and-portfolio/drawdown-stress-tail-and-regime-risk.md
sources:
  - https://doi.org/10.1111/jofi.12513
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
---

# 绩效度量与归因

绩效报告同时给出总收益、CAGR、年化波动、最大回撤及持续时间、Sharpe/Sortino/Calmar、期望短缺、偏度、峰度、换手、成本和在场率。指标必须注明现金利率、年化天数、样本区间与样本身份。

归因把变化拆成市场方向、资产选择、持现金、波动率缩放、费用/滑点和无法解释残差。案例与现金、BTC 持有、ETH 持有和 BTC/ETH 等权比较，使用同一开始日和计价货币。

单一比率不足以排名策略。样本短、厚尾或多次筛选会令比率不稳定；应报告最差子时期、风险路径和反事实基准。paper 与历史重放的差异也必须归因。
