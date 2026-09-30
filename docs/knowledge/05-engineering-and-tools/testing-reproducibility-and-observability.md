---
id: testing-reproducibility-observability
title: 测试、可复现性与可观测性
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - research-data-reporting-pipeline
related:
  - security-backup-and-disaster-recovery.md
  - ../06-production-discipline/incident-change-and-model-risk.md
  - ../../practice/playbooks/handle-drawdown-data-or-venue-incident.md
sources:
  - https://docs.pytest.org/en/stable/how-to/parametrize.html
  - https://csrc.nist.gov/pubs/sp/800/218/final
  - https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final
---

# 测试、可复现性与可观测性

## 测试优先级

1. **不变量**：权重非负、总敞口不超限、现金不因费用凭空增加。
2. **时间性**：信号使用过去数据，`t` 信号不能在同一 close 成交。
3. **经济性**：增加费用不能提高其他条件相同的最终权益；BTC→ETH 有两腿成本。
4. **幂等性**：重复 bar 不产生第二条 paper 记录。
5. **回归**：固定 fixture 的订单和指标摘要稳定。

## 可观测性

结构化日志包含时间、run ID、代码/配置版本、事件类型、资产、严重级别和原因。指标至少覆盖数据新鲜度、缺口、目标与实际模拟仓位、费用、回撤、重复/拒绝事件。日志不得包含密钥、完整账户标识或税务资料。

## 可复现验收

相同输入、配置、代码与锁文件应产生相同 decisions、orders 和 metrics 内容。运行目录带 manifest 与文件哈希；任何依赖升级都通过固定 fixture 回归比较并记录差异。
