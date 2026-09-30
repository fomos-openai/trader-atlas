---
id: case-risk-spec
title: BTC/ETH 案例风险规格
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - case-thesis
  - risk-budget-sizing
related:
  - paper-protocol.md
  - ../../knowledge/04-risk-and-portfolio/guardrails-kill-switches-and-retirement.md
  - ../../practice/templates/risk-budget.md
sources:
  - ../../../configs/btc-eth-spot-trend.yml
  - ../../../src/trader_atlas/strategy.py
---

# BTC/ETH 案例风险规格

## 组合约束

- 只做多（long-only），任一时点最多持 BTC、ETH 其中一种，其余为现金；不借贷、不做空、不使用衍生品。
- 年化波动率目标为 15%，按 365 日年化；这不是损失上限。单一风险资产权重硬上限为 99%，因此始终保留最少 1% 模型现金。
- 每周一评估；目标权重变化不足 5 个百分点不调仓，以限制无效换手。
- 基准单边成本为 10 bps fee 与 5 bps slippage，并同时审查总单边成本 25/40 bps 情景。

## 风险预算与独立资金边界

配置中的 `initial_cash=100000` 只是归一化研究本金，不是建议投入额。真实个人风险预算应由个人交易政策另行约束，且与生活费、税款、应急金和长期投资账户隔离。波动率缩放不能覆盖跳空、流动性枯竭、交易平台冻结、稳定币脱锚或数据中断。

## 暂停条件

出现数据契约失败、信号时间穿越、制品哈希不一致、订单意向字段异常或代码/配置未审查变更，立即停止运行。若 paper 观察中的实现成本持续高于压力假设、归因无法解释或风险指标触及个人政策阈值，状态改为 `paused`，先保全证据再诊断。恢复需新 run ID、书面根因和独立复核；本案例不定义任何实盘解锁条件。
