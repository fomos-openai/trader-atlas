---
id: paper-ledger-order-state
title: Paper 账本与订单状态
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - research-data-reporting-pipeline
related:
  - ../06-production-discipline/research-to-paper-stage-gates.md
  - ../../case/btc-eth-spot-trend/paper-protocol.md
sources:
  - ../../../src/trader_atlas/engine.py
  - ../../../src/trader_atlas/artifacts.py
---

# Paper 账本与订单状态

本地 paper 只生成 target-allocation intentions，不连接网络、不创建真实订单、不假定成交。状态至少记录最后处理时间、代码/配置/数据版本、目标资产与权重、意向 ID、已处理事件和审计日志。

建议状态机为 `CREATED → VALIDATED → INTENT_RECORDED`，异常进入 `REJECTED` 或 `PAUSED`；不存在 `SENT`、`FILLED` 等外部交易状态。重复 run ID 或重复事件不得覆盖旧证据。

Paper 输出包括 decisions、intent-only orders、trial ledger、audit、manifest 与哈希。缺 bar、数据过期、配置不一致或无法解析时 fail closed。若未来需要逐 bar 持久状态，应先定义幂等键、原子提交和恢复协议，不能直接复用研究批处理当作实盘系统。
