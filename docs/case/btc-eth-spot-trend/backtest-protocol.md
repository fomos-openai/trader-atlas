---
id: case-backtest-protocol
title: BTC/ETH 案例回测协议
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - case-btc-eth
  - backtest-biases
related:
  - ../../practice/templates/backtest-review.md
  - ../../knowledge/03-data-and-research/out-of-sample-and-robustness.md
  - data-contract.md
  - results-interpretation.md
sources:
  - ../../../configs/btc-eth-spot-trend.yml
  - ../../../src/trader_atlas/strategy.py
  - ../../../src/trader_atlas/engine.py
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
---

# BTC/ETH 案例回测协议

此协议把一次研究运行与“确认性证据”分开。当前 CLI 提供严格数据验证、确定性回测、基准和成本压力，但不自动宣称完成样本外验证。

## 运行前冻结

记录 experiment ID、数据来源/许可/下载时间/哈希、起止日期、配置 commit、研究问题、主要指标、反证与停止条件。默认配置是 200 日 SMA、90 日动量、30 日波动率目标、周一调仓和 next-open 模拟成交；看到结果后更改任一项都属于新 trial。

## 基准运行

1. `validate-data`：确认 UTC 日历连续、OHLCV 合法、BTC/ETH 同日历且 warm-up 足够。
2. `research`：运行总单边成本 15/25/40 bps 情景。
3. 检查 `manifest.json`、`manifest.sha256`、`audit.jsonl` 和 `trial_ledger.jsonl`，再读取 metrics。
4. 比较现金、BTC 持有、ETH 持有和 BTC/ETH 等权基准。

## 必须人工审查

- 周一决策的 `signal_as_of` 必须早于 `decision_timestamp`；
- 下一开盘模拟成交，资产切换包含 SELL 与 BUY 两腿；
- 增加成本不得在同一订单路径下提高最终权益；
- gross exposure 不超过配置上限，组合只能持 BTC、ETH 之一或现金；
- warm-up 期不产生可执行交易；
- 相同输入、配置和代码产生相同 decisions/orders/metrics 内容。

## 样本外协议

把研究期、验证期和最终 holdout 的日期在查看 holdout 前写入 research brief。参数只在研究期提出；验证期用于排除脆弱规则；最终 holdout 只运行一次。由于 v0.1 CLI 未内置防篡改的日期门，执行者必须用版本化数据清单与独立 run IDs 保存边界，并在审查报告中明确这一限制。若再次查看 holdout 后调参，该段不再是样本外。

## 结论等级

- 数据或时间审查失败：`invalid`；
- 仅有可复现历史运行：`exploratory`；
- 冻结规则通过 holdout 与压力：`confirmatory-candidate`；
- 再通过逐时本地 paper：`paper-observed`。

任何等级都不得改写为“盈利保证”或“可实盘”。
