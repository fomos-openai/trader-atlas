---
id: risk-guardrails-kill-switch-stop
title: Guardrails、Kill Switch 与退役规则
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - risk-budget-sizing
  - drawdown-stress
related:
  - ../../practice/playbooks/start-pause-or-retire-paper-strategy.md
  - ../06-production-discipline/scale-pause-rework-or-retire.md
sources:
  - https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final
  - https://www.iosco.org/library/pubdocs/pdf/IOSCOPD734.pdf
---

# Guardrails、Kill Switch 与退役规则

Guardrail 限制正常运行范围；kill switch 在信息不可信或风险越界时停止新增动作；stop rule 决定暂停、重研或退役。三者必须在运行前定义。

## 硬性 Guardrails

- 资产只允许 BTC、ETH、现金；权重非负且总和不超过 1；
- 数据超过允许时效、缺 bar 或时区不一致时不生成新意向；
- 成本、价格或持仓无法解析时 fail closed；
- 同一 rebalance ID 只能记账一次；
- 参数或代码版本变化后不得沿用旧审批。

## Kill switch 触发器

组合或资产回撤越过个人政策阈值；paper 账本无法对账；数据源与备用源差异超限；平台状态或规则发生重大变化；出现未解释重复订单、负现金或超仓位；香港监管/税务边界变化影响当前活动。

触发后按顺序：停止生成新动作 → 冻结证据 → 标记受影响区间 → 评估是否能安全重放 → 记录决定。不要先修数据再保存现场。

## 恢复条件

只有根因明确、修复有测试、历史受影响范围已量化、重新运行结果经复核、恢复决定有记录时才能解除。纯粹因为价格反弹或错失机会不能解除 kill switch。

若机制失效、数据不可持续、成本/容量消除边际、运营复杂度超限或香港活动边界改变，应退役而非无限重做。退役保留最终版本、证据和原因，并确保默认命令无法误启动。
