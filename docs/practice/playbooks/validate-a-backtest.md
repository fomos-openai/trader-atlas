---
id: validate-backtest
title: 验证回测 Playbook
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - backtest-biases
related:
  - ../templates/backtest-review.md
  - ../../paths/02-stage-gates.md
sources:
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
---

# 验证回测 Playbook

## 先验证证据身份

确认 experiment ID、代码 commit、依赖锁、配置、输入哈希、数据区间和输出清单齐全。不能重现则直接 `rework`，无需讨论收益。

## 审查顺序

1. **时间**：逐字段核对何时可见；检查 signal lag 与成交时点。
2. **账本**：现金、数量、费用、资产切换和权益恒等式一致。
3. **摩擦**：手续费、滑点、延迟、无法成交和报价货币处理明确。
4. **选择**：列出尝试过的全部参数/区间，识别多重检验和样本外污染。
5. **稳健性**：时间拆分、参数邻域、子时期、成本倍增和数据扰动。
6. **风险**：最大回撤、恢复时间、尾部、集中、换手和最差时期。
7. **基准**：现金、BTC 持有、BTC/ETH 等权与简化策略均用同一口径。

## 强制反证

审查者至少写出三个可能使结论错误的解释，并指出现有证据是否排除。若收益来自单个极端时期、单一参数点或不可成交假设，结论为 `stop` 或 `rework`。

## 输出

使用回测审查模板给出 `pass`、`pass-with-limit`、`rework` 或 `stop`，并附证据路径。不得只写“看起来合理”。
