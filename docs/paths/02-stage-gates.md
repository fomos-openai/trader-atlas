---
id: stage-gates
title: 研究到本地 Paper 的阶段门
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - fast-track
related:
  - ../practice/playbooks/validate-a-backtest.md
  - ../knowledge/06-production-discipline/research-to-paper-stage-gates.md
sources:
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
  - https://www.nist.gov/publications/secure-software-development-framework-ssdf-version-11-recommendations-mitigating-risk
---

# 研究到本地 Paper 的阶段门

阶段门（stage gate）把“继续投入”变成证据决定。任何红线失败都应回退或结束，不以提高收益参数来补救。

| 阶段 | 必需证据 | 红线 | 通过后的动作 |
| --- | --- | --- | --- |
| G0 任务定义 | 假设、资产、频率、基准、成本、失败条件已冻结 | 用“看看能不能赚钱”代替问题 | 建立数据契约 |
| G1 数据就绪 | 时区、重复、缺失、异常、可用时点和来源已核验 | 无法说明一列何时可见；来源许可不清 | 编写最小回测 |
| G2 回测可信 | 信号滞后、费用/滑点、现金、资产切换均被模拟 | 前视、幸存者偏差、成交价不可实现 | 冻结基准参数 |
| G3 稳健性 | 样本外、子时期、参数邻域、成本/延迟压力测试 | 仅一个参数点有效；成本翻倍即失效 | 进入本地 paper |
| G4 Paper 可运行 | 逐 bar 账本、幂等重跑、异常暂停、每日对账 | 会静默跳过数据；历史信号可被重写 | 连续观察并归因 |
| G5 复盘 | 研究预期与 paper 差异有解释，规则没有漂移 | 亏损后临时改规则；未记录例外 | 保持、重研或退役 |

## 决策记录

每次门审只允许四种结论：`pass`、`pass-with-limit`、`rework`、`stop`。记录审查日期、证据路径、反对意见、下一复核日和负责人。`pass-with-limit` 必须写清限制，例如“只允许合成数据 CI，不允许以该结果评价收益”。

## 当前硬边界

本项目的终点是 G5 的本地 paper 复盘。任何连接真实交易所、生成可发送订单、保存凭据或投入真实资金的工作，都属于另一个需单独授权和重新审查的项目。
