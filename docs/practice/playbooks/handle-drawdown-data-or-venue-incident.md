---
id: playbook-handle-incident
title: 处理回撤、数据或平台事件
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - incident-change-model-risk
related:
  - ../templates/incident-postmortem.md
  - ../../knowledge/04-risk-and-portfolio/guardrails-kill-switches-and-retirement.md
sources:
  - https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final
---

# 处理回撤、数据或平台事件

## 0–15 分钟：控制

暂停新意向；记录检测时间、最后正常时间和当前 paper 状态；复制只读证据清单，不修改原始数据。若只是研究运行，也要冻结失败输入和日志。

## 分类

- `RISK`：回撤、暴露、费用或换手越界；
- `DATA`：缺失、重复、延迟、异常值、schema/时区变化；
- `VENUE`：平台状态、规则、价格源、提款或合规状态变化；
- `SYSTEM`：崩溃、重复处理、账本不平、依赖或存储失败。

严重度由潜在错误决策与证据完整性决定，不由是否已产生真实损失决定。

## 诊断与恢复

建立事件时间线；确定影响的 bar、运行与输出；找直接原因和控制缺口；修复后新增失败复现测试；从已知良好状态重放并比较哈希。只有对账一致、测试通过、根因与范围经复核后才能恢复。

## 关闭

记录经验、负责人、截止日和是否更新 guardrail。若无法证明影响边界，保持暂停或退役。平台/监管状态不明时，以官方来源和专业意见为准，不以社交媒体消息恢复。
