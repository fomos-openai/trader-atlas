---
id: strategy-selection
title: 策略家族与选择
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - crypto-spot-market-structure
related:
  - ../../case/btc-eth-spot-trend/thesis.md
  - ../../practice/playbooks/choose-market-and-strategy.md
sources:
  - https://doi.org/10.1016/j.jfineco.2011.11.003
  - https://www.bis.org/publications/fsi-paper-27-cryptoasset-service-providers-financial-intermediaries-risks-and-policy-approaches
---

# 策略家族与选择

策略选择应最小化证据与运营负担，而不是最大化回测曲线。

| 家族 | 机制 | 主要风险 | 首版适合度 |
| --- | --- | --- | --- |
| 趋势/时间序列动量 | 捕捉持续方向 | 横盘反复、反转跳空 | 高：规则简单、低频可做 |
| 横截面轮动 | 持有相对更强资产 | 资产少、相关性高、集中 | 中：只作为趋势后的选择层 |
| 均值回归 | 偏离后回归 | 结构性断裂、抄底失控 | 低：需更强微观结构证据 |
| 基差/资金费率 | 赚取期限或融资差 | 杠杆、清算、平台/对手方 | 暂缓：不符合首版现货边界 |
| 波动率/期权 | 风险溢价与凸性 | 非线性、流动性、定价与保证金 | 暂缓 |
| 被动配置/再平衡 | 风险分散与纪律 | 同跌、再平衡成本 | 可作基准，不作首个主动策略 |

## 五项选择评分

每项 0–2 分：机制可解释、数据可得且 point-in-time、成本后仍有边际、尾部风险可承受、运营复杂度与个人时间匹配。任何一项为 0 都不得用总分掩盖。

## 首版选择

BTC/ETH 现货趋势轮动的价值在于：资产少、规则透明、换手低、无需杠杆，可用同一代码演示数据契约、回测、成本、风险和 paper 账本。它不是因为“收益最高”而被选中，而是最适合作为研究系统的验收载体。
