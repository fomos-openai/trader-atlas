---
id: knowledge-engineering-tools-home
title: 工程与工具
status: reviewed
last_reviewed: 2026-10-01
prerequisites:
  - knowledge-data-research-home
related:
  - stack-selection.md
  - research-data-and-reporting-pipeline.md
  - paper-ledger-and-order-state.md
  - testing-reproducibility-and-observability.md
  - security-backup-and-disaster-recovery.md
sources:
  - https://packaging.python.org/en/latest/guides/
  - https://csrc.nist.gov/pubs/sp/800/218/final
---

# 工程与工具

工具选择服务于可复现和可审计，不服务于技术炫技。首版采用单仓库、单 Python package、配置驱动、CSV 输入和文件化输出；不引入数据库、分布式队列或交易所 SDK。

本域交付：可锁定依赖的 Python 环境、纯函数化信号与回测核心、逐 bar 本地 paper 状态机、自动测试、结构化日志、秘密隔离和恢复方案。只要单机能可靠完成，就不增加基础设施。
