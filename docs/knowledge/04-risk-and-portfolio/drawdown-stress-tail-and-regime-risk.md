---
id: drawdown-stress
title: 回撤、压力、尾部与市场状态风险
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - risk-budget-sizing
related:
  - liquidity-capacity-and-counterparty.md
  - guardrails-kill-switches-and-retirement.md
sources:
  - https://www.bis.org/publ/bppdf/bispap138.pdf
  - https://www.iosco.org/library/pubdocs/pdf/IOSCOPD734.pdf
---

# 回撤、压力、尾部与市场状态风险

## 回撤不是单一数字

同时记录峰值到谷底幅度、持续时间、恢复时间和发生时的市场状态。历史最大回撤只是已观察下限，不是未来上限。若策略在快速反转中频繁换仓，应单独分析 whipsaw 序列，而非只看年度收益。

## 场景压力

- BTC/ETH 单日或多日急跌，同时相关性趋近 1；
- 趋势信号刚转空后价格快速 V 型反弹；
- 费用和价差为基准的 3 倍；
- 平台暂停交易或提款，无法按计划转现金；
- 数据延迟、重复或少一根 bar；
- 本地系统中断后恢复，存在重复意向订单风险。

压力结果至少输出损失、最大敞口、无法执行的动作和恢复步骤。

## 输出

每个场景记录冲击、持续时间、成交假设、权益路径、最大敞口、无法执行动作与恢复条件。不要只汇报最终收益；同样的终值可能对应完全不同的中途风险。历史未出现过的场景也应纳入，例如数据与平台故障和价格冲击同时发生。

市场状态（regime）切片用于诊断，不用于事后选择最好时期。预先定义方向与波动切片并报告全部结果；尤其观察横盘 whipsaw、急跌后 V 型反弹和 BTC/ETH 同跌。历史最大回撤只是已观察下限，不是未来上限。
