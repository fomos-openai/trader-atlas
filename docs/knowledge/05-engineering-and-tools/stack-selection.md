---
id: stack-selection
title: 技术栈选择
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - knowledge-engineering-tools-home
related:
  - research-data-and-reporting-pipeline.md
  - paper-ledger-and-order-state.md
  - ../../case/btc-eth-spot-trend/index.md
sources:
  - https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
  - https://docs.python.org/3/library/venv.html
  - https://numpy.org/doc/stable/reference/random/index.html
---

# 技术栈选择

## 最小栈

- Python 3.12：稳定、生态成熟；版本在 `pyproject.toml` 声明。
- `uv` 与提交的 `uv.lock`：创建环境、锁定依赖和运行命令。
- pandas / NumPy：表格、时间序列与数值计算。
- PyYAML：读取人类可审阅配置。
- pytest：单元、性质与 smoke tests。

首版不需要 Jupyter 作为权威执行入口。Notebook 可用于探索，但最终规则必须进入模块与测试；结果由 CLI 生成。

## 模块边界

`data` 只负责读取、校验与标准化；`signals` 只从历史数据生成目标；`backtest` 负责事件顺序、成交和账本；`paper` 逐 bar 更新不可回写状态；`metrics` 从账本计算指标；`cli` 只编排。模块不隐式联网，不读取全局密钥，不以当前时间改变历史回测。

## 可复现原则

- 所有策略参数来自版本化配置；
- 输入数据以 SHA-256 和 schema 绑定；
- 输出目录包含 run manifest；
- 随机步骤使用显式 `numpy.random.Generator` 和 seed；本案例核心算法应为确定性；
- 同一输入、配置、代码和依赖必须产生相同订单与指标。

工程复杂度的升级条件是现有设计无法通过已记录的可靠性或性能验收，而不是“未来可能需要”。
