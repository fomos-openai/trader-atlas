---
id: case-paper-protocol
title: BTC/ETH 案例本地 Paper 协议
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - case-backtest-protocol
  - research-to-paper
related:
  - risk-spec.md
  - results-interpretation.md
  - ../../practice/templates/paper-runbook.md
sources:
  - ../../../src/trader_atlas/cli.py
  - ../../../src/trader_atlas/engine.py
  - ../../../configs/btc-eth-spot-trend.yml
---

# BTC/ETH 案例本地 Paper 协议

本仓库的 `paper` 是离线目标配置意向（allocation intent）生成器，不连接交易所、不读取账户、不模拟真实排队，也不产生 fill。它验证研究规则能否在逐时输入上稳定重放，而不是验证可成交收益。

## 每次运行

1. 在计划决策时点后锁定输入数据，记录文件哈希与来源状态；先运行 `validate-data`。
2. 使用已批准配置执行 `trader-atlas paper`，为每次观察指定新的 run ID，禁止覆盖旧目录。
3. 检查 `orders.csv`：状态只能是 `INTENT_ONLY`，`network_used=false`、`fill_assumed=false`，且不得出现 `execution_price`。
4. 核对 `signal_as_of` 早于 `intended_execution_timestamp`，资产属于白名单，目标权重不超过 0.99。
5. 在运营复盘中记录“本来会做什么”、当时可见行情、人工可得报价与偏差；不要把事后成交价写回原始意向。

## 观察窗口与退出

开始前冻结最短观察时长和最少决策次数，避免因短期好坏任意结束。配置、代码、数据定义或观察方法变化时，关闭原 cohort 并开启新 trial。数据失败或意向异常立即暂停；规则长期没有触发不是故障，但须按期复核适用性。

完成本地 paper 只能得到 `paper-observed` 证据：它不授权接入 API 或实盘下单。任何实盘设计都属于仓库当前范围之外的新项目，需要单独监管、账户、密钥、执行和资本审批。
