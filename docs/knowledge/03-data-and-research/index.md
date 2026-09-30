---
id: knowledge-data-research-home
title: 数据与研究
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - knowledge-markets-strategies-home
related:
  - statistics-and-time-series.md
  - hypotheses-and-trial-ledger.md
  - data-contract-quality-and-lineage.md
  - backtest-biases-and-cost-models.md
  - out-of-sample-and-robustness.md
  - performance-measurement-and-attribution.md
sources:
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
  - https://doi.org/10.1093/rfs/hhv059
---

# 数据与研究

研究的目标不是证明策略有效，而是高效排除错误解释。每个结果都要能追溯到问题、数据版本、可用时点、代码、配置和检验次数。

本域依次回答：

1. [统计与时间序列口径](statistics-and-time-series.md)；
2. [把想法写成假设并登记全部试验](hypotheses-and-trial-ledger.md)；
3. [保证数据质量与血缘](data-contract-quality-and-lineage.md)；
4. [识别回测偏差并建模成本](backtest-biases-and-cost-models.md)；
5. [做样本外与稳健性验证](out-of-sample-and-robustness.md)；
6. [统一绩效度量和归因](performance-measurement-and-attribution.md)。

最小研究包由 `research brief + data manifest + locked config + run manifest + metrics + limitations` 组成。缺少任一项时，结果只能作为探索，不能进入阶段门评审。
