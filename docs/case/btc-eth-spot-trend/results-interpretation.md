---
id: case-results-interpretation
title: BTC/ETH 案例结果解读
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - case-backtest-protocol
  - performance-measurement-attribution
related:
  - paper-protocol.md
  - ../../practice/templates/backtest-review.md
  - ../../knowledge/03-data-and-research/out-of-sample-and-robustness.md
sources:
  - ../../../src/trader_atlas/metrics.py
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
---

# BTC/ETH 案例结果解读

## 阅读顺序

先读数据验证与 manifest，再核对决策/订单时间，最后看绩效。一个可重复的高收益结果若来自未来信息、错位价格或错误成本，仍是无效结果。将总单边成本 15/25/40 bps 情景分别与现金、BTC 持有、ETH 持有、BTC/ETH 等权基准比较，并明确区间和样本内/样本外标签。

## 指标语义

累计收益、年化收益、年化波动率、Sharpe、最大回撤、换手和执行成本分别回答不同问题。仓库 Sharpe 使用零现金利率，只适合同一实现内比较；最大回撤是观测样本的路径统计，不是未来最大损失。还应检查资产选择贡献、现金暴露、极端日依赖、交易次数与成本占毛收益比例。

## 结论模板

结论至少说明：数据版本与期间、规则/配置 commit、基准、成本假设、trial 数、holdout 是否未被重复查看、最强反证、未覆盖风险及下一步。若结果仅在单一参数点成立、40 bps 单边成本下失效或少数行情贡献绝大部分收益，应判为脆弱，而非挑选有利图表。

合成测试数据只证明程序行为，不能用于投资推断；历史真实数据也只能支持“在这些假设下曾发生”。本案例没有默认绩效数字，也不提供预期收益或未来表现保证。
