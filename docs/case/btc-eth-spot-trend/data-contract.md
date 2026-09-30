---
id: case-data-contract
title: BTC/ETH 案例数据契约
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - case-thesis
  - data-contract-quality
related:
  - backtest-protocol.md
  - ../../practice/templates/data-contract.md
sources:
  - ../../../data/README.md
  - ../../../src/trader_atlas/data.py
  - ../../../configs/btc-eth-spot-trend.yml
---

# BTC/ETH 案例数据契约

## 粒度与字段

输入是本地 long-form CSV 或 Parquet：每个 UTC 自然日、每个配置资产恰好一行。必需字段为 `timestamp,symbol,open,high,low,close,volume`；默认 `symbol` 只接受 `BTC`、`ETH`，报价资产语义为 USD。`timestamp` 表示日线开盘，必须是 `00:00:00Z`。

价格须为有限正数，成交量非负，并满足 `low <= open/close <= high`。同一资产不得有重复日期，BTC 与 ETH 日历必须完全一致且逐日连续；缺失价格不得前向填充。默认策略至少需要 201 个历史 bar 才能形成首个可决策信号。

## 时间与版本语义

周一 `decision_timestamp` 只能使用此前 bar，`signal_as_of < decision_timestamp`；模拟执行参考周一开盘价。数据集必须记录供应方、产品、时区、调整规则、下载时间、许可和原文件 SHA-256。修订历史数据时生成新版本，不覆盖旧文件或旧 manifest。

## 验收与隔离

先执行 `trader-atlas validate-data`，验证失败不得进入研究。校验通过只说明结构满足契约，不证明来源准确或没有幸存者偏差。受许可限制的行情、账户导出与 API 凭据保留在 Git 之外；公开仓库只保存契约、哈希和可再运行说明。
