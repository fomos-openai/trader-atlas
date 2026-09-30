---
id: incident-change-model-risk
title: 事件、变更与模型风险
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - discipline-monitoring-drift-attribution
related:
  - ../../practice/templates/incident-postmortem.md
  - ../../practice/playbooks/handle-drawdown-data-or-venue-incident.md
sources:
  - https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final
  - https://csrc.nist.gov/pubs/sp/800/218/final
---

# 事件、变更与模型风险

## 事件处理

按“发现 → 控制 → 保存证据 → 分析 → 修复 → 验证 → 恢复/退役”处理。第一动作通常是暂停新意向；不要先覆盖损坏文件。事件记录包括影响区间、首次/最后异常、受影响输出、临时控制、根因、修复 commit、验证和后续预防。

## 变更等级

- 文档或展示变化：不改变结果，可走轻量复核；
- 数据修正规则、依赖或性能优化：需要 regression test 和结果差异说明；
- 信号、成本、仓位、风险阈值或资产变化：视为策略新版本，重新回测、稳健性与 paper 门审。

“修 bug”也可能改变历史绩效，不能豁免结果比较。

## 模型风险与退役条件

机制不再可信；样本外/paper 持续与假设相反；成本或容量消除安全边际；数据/平台不可可靠获得；规则复杂度超过个人运营能力；香港监管或税务边界使活动不合适。

退役不是删除。冻结最终版本、证据、原因和可恢复说明；从默认运行列表移除，并确保后续不会误启动。
