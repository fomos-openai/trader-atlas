---
id: operating-review
title: 日、周、月与季度运营复盘
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - research-to-paper
related:
  - ../../practice/templates/trading-review.md
  - monitoring-drift-and-attribution.md
sources:
  - ../01-opc-operating-model/decision-journal-and-review.md
---

# 日、周、月与季度运营复盘

## 每个新 Bar / 每日

检查数据新鲜度、schema、最后处理时间、目标与模拟持仓、拒绝事件和日志完整性。无新信号也要留下 heartbeat；异常未解决时维持 pause。

## 每周

核对订单、费用、换手与权益；复查一次人工例外是否发生；记录与冻结回测重放的差异；安排数据和状态备份。周报不根据短期收益改参数。

## 每月

做收益/风险归因，更新回撤与压力场景，检查数据源、依赖和平台状态；统计实验数量、失败率、重复工作和未关闭事件。把“学到了什么”写成可复用规则。

## 每季度

重新审视优势假设、资金跑道、香港监管/税务资料、容量和继续/退役决定；执行一次从空环境恢复；核对知识库外链与官方资料日期。任何 `review_due` 到期页面优先处理。

复盘的目标是减少未知和规则例外，不是为每次波动寻找故事。若没有足够新证据，最合理的季度决定可以是“不变”。
