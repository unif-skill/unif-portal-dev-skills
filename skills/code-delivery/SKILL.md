---
name: code-delivery
description: 在 Portal、相关服务或 @unif RN／原生鸿蒙库准备或执行提交、推送、PR/MR、合并、发布、分支清理，或核对这些操作的交付条件时使用。单纯查询作业状态不触发。
---

# 交付规范

按当前授权和实际工程配置交付。本目录携带 Unif 组织约定及必要验收依据，可独立使用；执行命令和发布方式从目标工程的 AGENTS.md、贡献说明、检查脚本和 workflow 取得。

## 按交付对象读取

| 本次对象 | 本技能资料 |
|---|---|
| Unif RN 库的组织接入、命名与发布 | [包命名](references/package-naming.md)、[GitHub 采用](references/github.md)、[发布约定](references/publishing.md)；非敏感默认值见[组织资产](assets/organization.json) |
| RN 客户端及库的技术证据 | [RN 验证](references/rn/testing.md) |
| 原生鸿蒙、HAR 与共享核心 | [鸿蒙验证](references/harmony/testing.md)；按实际 OHPM／HAR 配置交付，不套 RN 组织资产或 npm 接线 |
| Python 后端的进程、资源和部署证据 | [后端验证](references/backend/validation.md)；不套 RN 包命名或发布身份 |
| 跨仓契约、结果与消费者兼容 | [交接契约](references/common/contracts.md)、[验证范围](references/common/verification.md) |

已有且仍有效的依据直接复用；提交、配置或目标变化后只补受影响核对。定向验证不替代工程 required 门禁，所有证据对应本次提交与实际执行层级。

## 操作边界

提交、推送、合并、发布和部署分别核对授权。保留无关工作区修改，检查实际暂存内容；合并核对当前 head 与 required 结果，分支清理核对内容、占用和远端回执。已有条件授权满足后继续，不因加载规范重复审批。

资料取得不启动重复测试或设计。报告实际完成的交付步骤、修订和未验证范围，不将本地构建、绿色 CI 或安装结果作为设备与真实业务验收。生成资料溯源见 references/source.json。
