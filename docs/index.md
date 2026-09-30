---
id: start-here
title: Trader Atlas 知识库
status: reviewed
last_reviewed: 2026-10-01
prerequisites: []
related:
  - paths/01-fast-track.md
  - knowledge/index.md
  - case/btc-eth-spot-trend/index.md
sources:
  - ../DISCLAIMER.md
---

# Trader Atlas 知识库

这是一套面向有工程与交易经验者的独立交易员（One-Person Company, OPC）学习与研究系统。目标不是寻找“稳赚策略”，而是把交易工作变成一条可审计的证据链：问题定义、数据、规则、回测、风险预算、本地 paper trading、复盘与停止。

## 从哪里开始

1. 先走[最短成长路径](paths/01-fast-track.md)，确定时间、资金与风险边界。
2. 用[阶段门](paths/02-stage-gates.md)决定项目能否继续；不因沉没成本跳过门槛。
3. 按六个知识域补齐能力：OPC 经营、数字资产与策略、数据研究、风险组合、工程工具、研究纪律。
4. 使用[BTC/ETH 现货趋势轮动案例](case/btc-eth-spot-trend/index.md)跑通离线研究和本地 paper；案例不连接交易所，也不构成投资建议。
5. 将自己的假设写入[研究简报](practice/templates/research-brief.md)，再进入实验。

## 六个知识域

| 领域 | 要回答的问题 | 必须产物 |
| --- | --- | --- |
| [OPC 经营模型](knowledge/01-opc-operating-model/index.md) | 为什么做、能承受什么、香港边界是什么 | 个人交易政策、资金跑道、记录制度 |
| [市场与策略](knowledge/02-markets-and-strategies/index.md) | 交易什么、优势从哪里来、成本与平台风险如何处理 | 市场/策略选择卡 |
| [数据与研究](knowledge/03-data-and-research/index.md) | 结论是否可重现、是否有泄漏或过拟合 | 数据清单、实验日志、样本外报告 |
| [风险与组合](knowledge/04-risk-and-portfolio/index.md) | 最坏情形是什么、何时降险或停止 | 风险预算、压力测试、停止规则 |
| [工程与工具](knowledge/05-engineering-and-tools/index.md) | 如何把研究做成可靠流水线 | 可复现环境、测试、日志与备份 |
| [研究纪律](knowledge/06-production-discipline/index.md) | 如何从研究进入本地 paper 并持续复盘 | paper 账本、归因、事件与退役记录 |

## 使用边界

- 当前范围止于研究和本地 paper trading；不提供实盘下单、托管或代客管理能力。
- 所有收益数字都必须同时给出数据区间、成本模型、样本内/样本外标记和最大回撤；单一 Sharpe ratio 不是上线理由。
- 香港监管与税务内容只提供研究边界，不能替代持牌专业人士意见；使用前检查页面的 `as_of` 与 `review_due`。
- 真实 API 密钥、账户号、持仓、税务文件与受许可限制的行情不得提交到公开仓库。

## 内容状态

`status: reviewed` 表示结构、来源和表述经过仓库级检查，不表示监管、税务或投资结论永久有效。任何规则变化、数据源变化或策略参数变化都要触发重新审查。
