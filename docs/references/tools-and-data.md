---
id: references-tools-data
title: 工具与数据选择
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - stack-selection
related:
  - ../case/btc-eth-spot-trend/index.md
  - ../knowledge/03-data-and-research/data-contract-quality-and-lineage.md
sources:
  - https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
  - https://pandas.pydata.org/docs/user_guide/timeseries.html
  - https://numpy.org/doc/stable/reference/random/index.html
  - https://docs.pytest.org/en/stable/
---

# 工具与数据选择

## 当前选择

| 能力 | 工具 | 选择理由 | 不承担的职责 |
| --- | --- | --- | --- |
| 运行环境 | Python 3.12 + `uv` | 依赖锁定、命令简洁 | 不保证跨版本 bit-level 浮点一致 |
| 表格/时间序列 | pandas | 清晰的索引、rolling 与 IO | 不替代数据契约 |
| 数值计算 | NumPy | 稳定数组与统计基础 | 不把随机搜索作为默认方法 |
| 测试 | pytest | fixture、parametrize、清晰失败 | 测试通过不证明策略有效 |
| 配置 | YAML | 人类可读、可版本化，主配置路径固定 | 不保存秘密 |
| 数据 | 本地 CSV/Parquet | 离线、可哈希、可审计 | 不自动下载或再分发受许可数据 |

## 数据源选择清单

记录提供方、法律实体、市场/venue、字段语义、时区、历史修订、限频、许可、保存/再分发权、费用、故障历史和替代源。免费并不等于允许再分发；公开仓库只提交 schema、下载说明和哈希，不提交未经明确授权的行情。

## 为什么首版不选更重工具

数据库、流处理、云调度、向量化回测框架和交易所统一 API 会扩大依赖与故障面。当前日线双资产数据可以在内存中严格验证，纯 Python 事件循环更容易审计成交顺序。只有经测量的性能或可靠性问题出现后才升级。

## 升级触发器

数据规模超出内存、需要跨市场日历、paper 状态需要并发写入，或现有实现无法在目标时间内完成且 profiling 给出瓶颈。升级必须保留相同数据/订单契约和 regression fixture。
