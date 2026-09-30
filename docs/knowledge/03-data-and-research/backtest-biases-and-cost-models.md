---
id: backtest-biases
title: 回测偏差与成本模型
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - data-contract-quality
related:
  - out-of-sample-and-robustness.md
  - ../05-engineering-and-tools/testing-reproducibility-and-observability.md
sources:
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
  - https://doi.org/10.1111/1468-0262.00152
---

# 回测偏差与成本模型

## 必查偏差

- **Look-ahead bias**：使用尚未完成的 bar、未来修订值或同一收盘信号/成交。
- **Selection bias**：只展示表现最好的参数、区间或指标。
- **Survivorship bias**：用今天仍存在的资产或平台重构历史。
- **Data snooping**：反复查看样本外并继续调参，使其事实上变成样本内。
- **Implementation bias**：假定无限流动性、零失败、零延迟或可在理论中间价成交。

## 事件顺序

一根 bar 的正确顺序是：读取截至 `t` 已完成数据 → 计算信号 → 生成 `t+1` 目标 → 用预先定义的 `t+1` 价格与成本模拟成交 → 更新现金和持仓 → 记录权益。代码应以测试证明信号整体延迟，而不是靠注释保证。

## 成本与记账

费用在每条成交腿上计算；BTC→ETH 是先卖后买。现金、未投资时段、最小交易量、数量精度、无法成交和调仓阈值应明确。所有收益使用同一计价货币，避免把价格收益与资产数量变化混在一起。

## 可复现运行

每次运行保存：代码 commit、Python/依赖锁、配置哈希、输入数据哈希、随机种子（如有）、开始/结束时间、输出清单和摘要哈希。相同输入应产生相同订单、权益与指标；若因库升级发生变化，应被 regression test 捕获并解释。

可复现并不证明策略有效，但不可复现足以否定研究证据。
