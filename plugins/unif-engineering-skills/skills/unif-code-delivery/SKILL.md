---
name: unif-code-delivery
description: 在 Portal、相关服务或 @unif RN／原生鸿蒙库准备或执行提交、推送、PR/MR、合并、发布、分支清理，或核对这些操作的交付条件时使用。单纯查询作业状态不触发。
---

# 交付规范

从目标工程的 AGENTS.md、脚本与 workflow 确认交付入口，核对本轮已确认的范围、工作区、提交及验证结果。

## 按交付对象读取

| 本次对象 | 本技能资料与工程依据 |
|---|---|
| Unif RN 库的组织接入、命名与发布 | [包命名](references/package-naming.md)、[GitHub 采用](references/github.md)、[发布约定](references/publishing.md)；非敏感默认值见[组织资产](assets/organization.json) |
| Portal RN 客户端的技术证据 | [Portal 验证](references/rn/testing.md) |
| Unif RN 库的技术证据 | 本库采用的规范、检查脚本、产物与公开消费者记录；共同验证依据按下文选读 |
| 原生鸿蒙、HAR 与共享核心 | [鸿蒙验证](references/harmony/testing.md)；按实际 OHPM／HAR 配置交付，不套 RN 组织资产或 npm 接线 |
| Python 后端的类型检查、进程、资源和部署证据 | [后端验证](references/python/validation.md)；不套 RN 包命名或发布身份 |
| 跨仓契约、结果与消费者兼容 | [交接契约](references/common/contracts.md)、[依赖治理](references/common/verification.md#71-依赖治理)、[变更影响](references/common/verification.md#73-变更影响) |

按[测试责任](references/common/verification.md#72-测试责任)说明本次提交的实际验证范围。已有结果仍适用时复用，合并前核对当前提交的 required 检查。

## 操作边界

提交、推送、合并、发布和部署分别核对授权。保留无关工作区修改，检查实际暂存内容；合并核对当前 head 与 required 结果，分支清理核对内容、占用和远端回执。已有条件授权满足后继续，不因加载规范重复审批。

交付说明写明实际完成的操作、修订和待验收内容。
