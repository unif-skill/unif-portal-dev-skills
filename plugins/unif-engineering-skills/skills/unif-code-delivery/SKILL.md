---
name: unif-code-delivery
description: 准备一次具体的 Unif 交付，或执行已获授权的提交、推送、合并、发布、部署或分支清理时使用。只查 CI 状态或维护 GitHub 设施时使用相应工具。
---

# Unif 代码交付

先核对本次授权的操作、目标仓库和分支，从工程 AGENTS.md、脚本与 workflow 确认交付入口。针对待提交的内容或当前 PR 修订检查证据，保留工作区中的无关修改。

## 核对本次要交付的内容

| 对象 | 交付前核对什么 |
|---|---|
| Portal RN 应用 | 从工程 `scripts/README.md` 选择覆盖本次功能、适配和实际消费者的检查。找出暂存差异对应的行为证据。[Portal 验证](https://github.com/unif-design/unif-platform-architecture/blob/main/PORTAL_DEVELOPMENT.md#5-规则执行与定向验证)、[消费者验证](https://github.com/unif-design/unif-platform-architecture/blob/main/PORTAL_STRUCTURE.md#6-开发维护与定向验证) |
| Unif RN 库 | 按[包命名](references/package-naming.md)和[发布约定](references/publishing.md)核对库版本、包内容和使用它的应用或示例。本库的[组织约定](references/github.md)和[非敏感组织资产](assets/organization.json)供实际交付或 GitHub 设施接入使用。设施维护由 `uni-github-delivery-setup` 承接。 |
| 原生鸿蒙和 HAR | 核对实际 OHPM／HAR 配置，记录包导入和原生宿主结果。共享核心的证据要对应这次采用的修订。[鸿蒙验证](https://github.com/unif-design/unif-platform-architecture/blob/main/HARMONY_DEVELOPMENT.md#5-验证与交付) |
| Python 服务 | 核对工程解释器运行的类型检查，以及涉及的进程、存储、镜像或部署结果。[后端验证](https://github.com/unif-design/unif-platform-architecture/blob/main/PYTHON_DEVELOPMENT.md#6-验证与交付) |
| 跨仓契约 | 核对生成物版本、消费者锁定的修订及其交付顺序。公共依据见 `$unif-platform-rules` 的 `references/architecture/contracts.md` 和 `references/architecture/verification.md#73-变更影响`。 |

## 执行已授权的操作

1. 核对已有结果是否覆盖待交付修订。需要选择或补跑验收检查时，用 `uni-verify-change`。
2. 执行已获授权的操作。合并前复核当前 PR 最新提交的必需检查。清理分支前确认它的最新提交、内容是否已交付以及是否仍有工作区占用。
3. 记录实际操作、修订、远端回执和仍待验收的内容。提交、推送、合并、发布、部署和清理各依本次授权。
