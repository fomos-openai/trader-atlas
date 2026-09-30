---
id: case-thesis
title: BTC/ETH 现货趋势轮动研究假设
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - case-btc-eth
  - strategy-selection
related:
  - data-contract.md
  - backtest-protocol.md
  - ../../practice/templates/research-brief.md
sources:
  - ../../../configs/btc-eth-spot-trend.yml
  - https://doi.org/10.1016/j.jfineco.2011.11.003
---

# BTC/ETH 现货趋势轮动研究假设

## 可证伪命题

在仅持 BTC、ETH 或现金的约束下，先用长期趋势过滤风险资产，再在合格资产中选择中期动量较强者，并按近期波动率缩放仓位，可能比无条件长期满仓减少部分深度回撤。这里的“可能”必须由冻结规则、样本外数据和成本压力检验；时间序列动量的跨资产论文只提供研究动机，不能证明数字资产或本规则未来有效。

## 冻结的机制

每个周一决策点只读此前已完成的日线。资产须同时满足：最新收盘价高于 200 日简单移动平均线（SMA），且 90 日收益为正。若两者都合格，选择 90 日动量较高者；均不合格则持现金。目标权重为 `15% / 过去 30 日年化波动率`，再截断到 99%；目标变化不足 5 个百分点时不调仓。

该设计分开回答三个问题：长期趋势决定是否承担方向风险，相对动量决定承担哪一种风险，波动率目标决定承担多少。任何阈值或周期变化都构成新 trial，不能用最终 holdout 反复优化。

## 主要反证

- 扣除现实成本后，样本外表现不优于简单、可交易的基准；
- 收益集中于少数日期、单一资产或单一市场状态；
- 参数轻微变化、日期平移或成本提高即令结论反转；
- 信号在可获得时点不可计算，或 next-open 执行不具可行流动性；
- 减少回撤的代价是长期现金拖累，风险调整后也无补偿。

研究输出只能标记为 `exploratory`、`confirmatory-candidate` 或 `paper-observed` 等证据等级，不得写成收益承诺。
