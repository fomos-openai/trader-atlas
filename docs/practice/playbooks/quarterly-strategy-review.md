---
id: quarterly-strategy-review
title: 季度策略审查 Playbook
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - operating-review
related:
  - ../templates/trading-review.md
  - ../../knowledge/06-production-discipline/scale-pause-rework-or-retire.md
sources:
  - ../../knowledge/06-production-discipline/operating-review-routines.md
---

# 季度策略审查 Playbook

## 准备

冻结季度末账本和 run manifests；汇总 paper 意向、规则例外、数据/系统事件、成本压力、回撤与归因；复核香港监管/税务页面和平台状态日期。

## 审查

1. 机制是否仍可解释，是否出现反证；
2. 数据、代码、配置和输出能否从空环境恢复；
3. paper 与冻结回测差异是否全部归因；
4. 风险、容量、平台与运营时间是否仍在政策内；
5. 参数或人工例外是否发生未审批漂移；
6. 能力评分卡的最低项是否改善。

## 决定

只能选 `continue / scale-research-only / pause-and-rework / retire`。记录证据、限制、负责人和下次复核；短期收益不能单独支持继续或扩展。当前仓库不提供真实资金扩容决定。
