---
id: security-backup-disaster-recovery
title: 安全、备份与灾难恢复
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - stack-selection
related:
  - testing-reproducibility-and-observability.md
  - ../06-production-discipline/incident-change-and-model-risk.md
sources:
  - https://csrc.nist.gov/pubs/sp/800/218/final
  - https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final
---

# 安全、备份与灾难恢复

NIST SSDF 强调把安全纳入开发生命周期。当前案例不需要密钥；未来即使接入外部数据，也应使用环境变量或 secret store、最小权限、依赖锁定和漏洞扫描。禁止提交 `.env`、cookie、wallet seed phrase、账户和税务身份。

采用 3-2-1 备份：至少三份、两种介质、一份异地。代码可依赖 Git 远端，数据 manifest、paper 证据和税务记录需加密备份并限制访问。定义 RPO（可容忍丢失）与 RTO（可容忍恢复时间）。

每季度从空目录恢复代码、环境、配置和一个已知 run，验证 manifest 与哈希；演练结果进入事件记录。无法恢复的备份等于未验证。
