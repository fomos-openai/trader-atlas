---
id: backtest-review
title: 回测审查模板
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - validate-backtest
related:
  - research-brief.md
  - strategy-and-risk-card.md
sources:
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
---

# 回测审查模板

- Experiment / run ID：
- Code commit / lock / config / input hash：
- 独立复现命令与结果：

## 检查

- [ ] 字段可用时点与 signal lag 已证明
- [ ] 现金、持仓、费用和权益账本对平
- [ ] 费用、滑点、延迟和无法成交被建模
- [ ] 所有试验/参数数量已披露
- [ ] 样本外没有被重复用于调参
- [ ] 参数邻域、子时期、成本和数据压力已完成
- [ ] 与现金、持有、等权和简化策略公平比较
- [ ] 回撤、尾部、换手、容量和平台风险已报告

## 反证

1. 可能错误解释 / 当前证据：
2. 可能错误解释 / 当前证据：
3. 可能错误解释 / 当前证据：

## 结论

- 决策：`pass / pass-with-limit / rework / stop`
- 限制与未解决问题：
- 下一步 / 负责人 / 截止日：
- 审查人 / 日期：
