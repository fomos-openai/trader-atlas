---
id: discipline-monitoring-drift-attribution
title: 监控、漂移与归因
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - research-to-paper
related:
  - operating-review-routines.md
  - ../04-risk-and-portfolio/guardrails-kill-switches-and-retirement.md
sources:
  - https://www.nist.gov/publications/secure-software-development-framework-ssdf-version-11-recommendations-mitigating-risk
---

# 监控、漂移与归因

## 四类漂移

- **数据漂移**：缺口、延迟、来源字段或价格分布变化；
- **执行漂移**：模拟成交与原假设的延迟、费用和滑点差异；
- **风险漂移**：波动、相关、回撤、在场率或平台集中变化；
- **规则漂移**：人工例外、参数或代码与审批版本不一致。

监控应先问“系统是否仍在按定义运行”，再问“是否赚钱”。

## 归因

将组合变化拆成：BTC/ETH 方向暴露、资产选择、持现金、换仓成本、数据/执行偏差和残差。对于趋势轮动，至少比较实际 paper 账本与同日期的冻结回测重放；差异若无法解释，暂停而不是归因给市场噪声。

## 阈值

阈值来自个人政策和策略卡，并分为 warning、pause、stop。Warning 触发调查但不改变历史；pause 停止新意向；stop 进入退役或重新研究。避免用滚动指标自动放宽阈值，因为那会把风险政策变成追随市场的参数。
