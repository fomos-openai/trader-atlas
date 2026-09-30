---
id: practice-home
title: 实践区：Playbooks 与模板
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - knowledge-home
related:
  - playbooks/choose-market-and-strategy.md
  - playbooks/validate-a-backtest.md
  - playbooks/start-pause-or-retire-paper-strategy.md
  - templates/research-brief.md
  - templates/personal-trading-policy.md
sources:
  - ../paths/02-stage-gates.md
  - ../knowledge/06-production-discipline/index.md
---

# 实践区：Playbooks 与模板

Playbook 规定“何时做、按什么顺序做、什么证据才算完成”；模板规定“结果必须记录哪些字段”。两者要配套使用，不能把勾选清单当成独立判断。

## Playbooks

- [选择市场与策略](playbooks/choose-market-and-strategy.md)：从约束和可验证优势出发，避免按历史收益排行榜选择。
- [验证回测](playbooks/validate-a-backtest.md)：先验证时间、数据与成本，再评价绩效。
- [启动、暂停或退役 Paper 策略](playbooks/start-pause-or-retire-paper-strategy.md)：把状态转换变成有证据的决策。
- [处理回撤、数据或平台事件](playbooks/handle-drawdown-data-or-venue-incident.md)：先隔离风险和保全证据，再定位根因。
- [季度策略审查](playbooks/quarterly-strategy-review.md)：定期选择继续、重研、暂停或退役。

## 模板

先完成[个人交易政策](templates/personal-trading-policy.md)和[研究简报](templates/research-brief.md)，再使用[策略与风险卡](templates/strategy-and-risk-card.md)、[数据契约](templates/data-contract.md)、[回测审查](templates/backtest-review.md)与[风险预算](templates/risk-budget.md)。进入本地 paper 后，持续维护 [Paper 运行手册](templates/paper-runbook.md)、[交易研究复盘](templates/trading-review.md)和[事件复盘](templates/incident-postmortem.md)。

所有模板填写件应有日期、owner、版本、关联 run/commit 和下一复核日；包含账户、密钥、持仓或受许可数据的填写件不得直接提交到公开仓库。
