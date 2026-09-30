---
id: research-to-paper
title: 研究到 Paper 的阶段门
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - out-of-sample-robustness
  - risk-guardrails-kill-switch-stop
related:
  - monitoring-drift-and-attribution.md
  - ../../practice/playbooks/start-pause-or-retire-paper-strategy.md
sources:
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
---

# 研究到 Paper 的阶段门

## 入场包

进入 paper 前冻结：策略与风险卡、代码 commit、依赖锁、配置、数据契约、样本外报告、压力测试、已知限制、停止规则和批准记录。Paper 期不得悄悄更改参数；任何变更生成新版本并重新通过前置阶段门。

## 逐 Bar 流程

1. 验证新 bar 完整、时区正确且晚于最后处理时间；
2. 计算只依赖历史的信号与目标仓位；
3. 应用风险 guardrails；
4. 以预设成交模型产生本地 simulated fill；
5. 原子写入订单、持仓、现金、费用和事件哈希；
6. 输出状态摘要和异常。

本地 paper 不请求交易所报价、不持有 API key、不发送订单。数据可以由人工下载后导入，确保边界清晰。

## 观察期

观察期应覆盖足够的调仓事件和至少一次无信号/持现金状态；固定日历天数不能替代事件数量。若市场长期单边导致未触发关键分支，用合成场景测试补充，但要与真实 paper 结果分开报告。
