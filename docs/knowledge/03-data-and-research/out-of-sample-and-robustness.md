---
id: out-of-sample-robustness
title: 样本外验证与稳健性
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - backtest-biases
related:
  - ../../practice/playbooks/validate-a-backtest.md
  - ../06-production-discipline/research-to-paper-stage-gates.md
sources:
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
  - https://doi.org/10.1111/1468-0262.00152
---

# 样本外验证与稳健性

稳健性不是“换几个参数仍盈利”，而是结论在合理的未知与摩擦下仍保留方向和风险价值。

## 最小检验集

1. **时间拆分**：按时间顺序分训练/设计期、验证期和一次性最终样本外期。
2. **Walk-forward**：只使用过去窗口决定当前规则；不从未来反向选择窗口。
3. **参数邻域**：趋势、动量与调仓参数在合理邻域形成平台，而非孤立尖峰。
4. **子时期与状态**：牛、熊、横盘、高/低波动分别报告，不以全样本平均掩盖。
5. **摩擦压力**：总单边成本 15/25/40 bps、延迟一 bar、部分无法成交。
6. **数据扰动**：缺失 bar、异常点、venue 替代数据和不同 UTC 边界。

## 证据等级

- `E0 想法`：只有机制描述。
- `E1 探索`：有可复现回测，但仍在调参。
- `E2 确认`：冻结规则通过预留样本、成本与参数邻域检查。
- `E3 Paper`：逐时运行并记录偏差、异常和规则遵守。

当前仓库最高只到 `E3`，不得用 “production/live ready” 描述。

## 结论模板

结论必须同时写支持证据、反证、最敏感假设、失败条件和下一步。若样本外较差，默认结论是证据不足；不允许立刻重新调参后仍称同一个样本为“样本外”。
