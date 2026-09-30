---
id: hypotheses-trial-ledger
title: 假设、实验协议与 Trial Ledger
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - statistics-time-series
related:
  - ../../practice/templates/research-brief.md
  - backtest-biases-and-cost-models.md
sources:
  - https://doi.org/10.1093/rfs/hhv059
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
---

# 假设、实验协议与 Trial Ledger

可研究假设包含机制、可观测预测、基准、适用条件和证伪条件。例如：“若中期方向持续性覆盖周频换仓成本，趋势轮动在预留样本上应改善回撤，而不只是提高总收益。”

查看最终样本前冻结资产、区间、信号、执行滞后、调仓、成本、现金、基准、主要指标和门槛。探索可以改变想法，但改变后生成新 trial ID，不能把修改后的假设伪装为事前设定。

Trial ledger 对每次运行保存：父假设、代码/配置/数据哈希、参数、看过的数据区间、结果、结论和状态。失败与中止运行也保留。只有完整披露尝试次数，才能讨论 multiple testing 与选择偏差。

最终 holdout 一旦用于调参便失去样本外身份。Ledger 应能回答“在得到这个结果前已经试过多少版本”。
