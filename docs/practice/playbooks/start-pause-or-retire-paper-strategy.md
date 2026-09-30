---
id: paper-runbook
title: 启动、暂停与退役 Paper 策略
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - research-to-paper
related:
  - ../templates/strategy-and-risk-card.md
  - ../templates/trading-review.md
sources:
  - ../../knowledge/06-production-discipline/research-to-paper-stage-gates.md
---

# 启动、暂停与退役 Paper 策略

## 启动

- G0–G3 阶段门已通过，策略与风险卡签署；
- 代码、配置、依赖、数据 schema 与样本外报告冻结；
- 使用全新状态目录完成一次 cold start 与一次重复 bar 测试；
- 确认没有网络下单依赖、API key 或真实账户标识；
- 记录 paper 版本、起始时间、观察目标和预定复核日。

## 暂停

任一 kill switch 触发时立即停止生成新意向，保留当前状态、日志和输入。状态标记为 `paused`，写明触发时间与原因。修复必须有测试和受影响区间分析，恢复使用新批准记录。

## 退役

退役前生成最终指标、差异归因、未解决问题、最终数据/代码哈希和原因。将状态设为 `retired`，移出默认任务，并验证普通启动命令不会重新运行。资料保持只读可追溯。

## 禁止事项

不得因短期亏损临时改信号；不得因短期盈利放宽风险；不得把 paper 成交当作实际可成交证明；不得从本 playbook 直接过渡到真实资金。
