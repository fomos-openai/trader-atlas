---
id: statistics-time-series
title: 统计与时间序列基础
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - knowledge-data-research-home
related:
  - hypotheses-and-trial-ledger.md
  - data-contract-quality-and-lineage.md
sources:
  - https://doi.org/10.1093/rfs/hhv059
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
---

# 统计与时间序列基础

金融收益常呈厚尾、波动聚集、序列相关与状态变化；均值和正态假设不足以描述风险。研究至少检查收益分布、滚动波动、下跌期相关、极端分位、缺失机制和有效样本长度。

## 时间顺序

移动窗口、滞后和重采样必须说明端点是否包含当前 bar。时间序列切分保持顺序，随机打乱会把未来状态泄漏到训练期。任何年化都要匹配 24/7 市场与实际观测频率。

## 多重检验

尝试的参数、资产、指标和起止日期越多，偶然得到漂亮结果的概率越高。Harvey、Liu 与 Zhu 对金融研究中的 multiple testing 提出更高证据门槛；Bailey 等人则给出 backtest overfitting 的量化框架。个人研究至少应保存所有试验，而非只保存胜者，并报告：

- 总共测试了多少想法与参数组合；
- 主要假设是否在试验前冻结；
- 哪些结果来自探索、哪些来自确认；
- 样本外数据是否只使用一次。

## 指标解释

均值、波动率和 Sharpe ratio 不足以描述偏态、厚尾与路径依赖。至少同时查看最大回撤、恢复时长、最差月/周、换手、在场率、尾部损失、与基准差异及结果的不确定区间。统计显著不等于经济可交易，经济可交易也不等于风险可承受。
