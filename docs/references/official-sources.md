---
id: official-sources
title: 官方与学术来源
status: reviewed
last_reviewed: 2026-10-01
prerequisites: []
related:
  - ../../DISCLAIMER.md
  - ../knowledge/01-opc-operating-model/hong-kong-regulatory-and-tax-boundaries.md
sources:
  - https://www.sfc.hk/en/Welcome-to-the-Fintech-Contact-Point/Virtual-assets/Virtual-asset-trading-platforms-operators
  - https://www.ird.gov.hk/eng/pdf/dipn39.pdf
  - https://www.iosco.org/library/pubdocs/pdf/IOSCOPD734.pdf
  - https://www.bis.org/publ/bppdf/bispap138.pdf
---

# 官方与学术来源

本页记录知识库使用的核心来源及用途；监管状态核验日期为 2026-10-01。引用表示来源支持某项事实或方法，不表示来源认可本仓库策略。

## 香港监管与税务

- [SFC：Virtual asset trading platform operators](https://www.sfc.hk/en/Welcome-to-the-Fintech-Contact-Point/Virtual-assets/Virtual-asset-trading-platforms-operators)：香港 VATP 发牌制度概览；页面显示 2025-01-16 更新，使用时再次核验。
- [SFC：Lists of virtual asset trading platforms](https://www.sfc.hk/en/Welcome-to-the-Fintech-Contact-Point/Virtual-assets/Virtual-asset-trading-platforms-operators/Lists-of-virtual-asset-trading-platforms)：持牌、申请、撤回/拒绝及关闭平台名单；名单持续更新，不能把申请等同持牌。
- [SFC：Do you need a licence or registration?](https://www.sfc.hk/en/Regulatory-functions/Intermediaries/Licensing/Do-you-need-a-licence-or-registration)：受规管活动与虚拟资产相关活动入口；具体事实应寻求专业意见。
- [SFC：Statement on virtual asset arrangements claiming to offer returns](https://www.sfc.hk/en/News-and-announcements/Policy-statements-and-announcements/Statement-on-virtual-asset-arrangements-claiming-to-offer-returns-to-investors)：回报、存款、staking 类安排的损失与 CIS 风险提示。
- [IRD：DIPN 39 — Digital Economy, Electronic Commerce and Digital Assets](https://www.ird.gov.hk/eng/pdf/dipn39.pdf)：数字资产利得税分析原则，2020-03 发布；不应抽取一句话替代事实分析。
- [HKMA：Updated Guidance on Provision of Custodial Services for Digital Assets](https://brdr.hkma.gov.hk/eng/doc-ldg/current/20260527-6-EN)：认可机构提供数字资产托管的预期标准，2026-05-27。

## 市场与风险

- [IOSCO：Policy Recommendations for Crypto and Digital Asset Markets](https://www.iosco.org/library/pubdocs/pdf/IOSCOPD734.pdf)：利益冲突、市场滥用、托管、跨境、技术风险与零售分销基准，2023。
- [BIS：Financial stability risks from cryptoassets in emerging market economies](https://www.bis.org/publ/bppdf/bispap138.pdf)：市场、流动性、信用、运营等风险分类，2023。
- [BIS FSI：Cryptoasset service providers as financial intermediaries](https://www.bis.org/publications/fsi-paper-27-cryptoasset-service-providers-financial-intermediaries-risks-and-policy-approaches)：收益、借贷、保证金和衍生品叠加风险，2026-04-23。

## 研究方法

- [Moskowitz, Ooi & Pedersen：Time Series Momentum](https://doi.org/10.1016/j.jfineco.2011.11.003)：传统期货市场的时间序列动量证据；不能直接外推为 BTC/ETH 收益承诺。
- [Bailey et al.：The Probability of Backtest Overfitting](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)：回测选择与过拟合风险。
- [Harvey, Liu & Zhu：…and the Cross-Section of Expected Returns](https://doi.org/10.1093/rfs/hhv059)：金融研究中的多重检验与证据门槛。
- [White：A Reality Check for Data Snooping](https://doi.org/10.1111/1468-0262.00152)：数据窥探下的模型评估。

## 工程与连续性

- [NIST SP 800-218 SSDF](https://csrc.nist.gov/pubs/sp/800/218/final)：安全软件开发实践，2022。
- [NIST SP 800-34 Rev. 1](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)：备份、恢复和连续性计划。

## 维护规则

监管来源至少季度复核，工具来源在依赖升级时复核，学术来源在核心结论变化或新增策略时复核。发现链接迁移时更新本页和 `link-registry.yml`，但保留来源标题与访问日期记录。
