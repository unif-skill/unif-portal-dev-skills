---
name: unif-rn-review
description: 在审查 Unif React Native 应用、@unif RN 库或共享核心的代码与构建配置，核对契约、状态、资源、故障证据和验证范围时使用。仅为回答事实问题阅读源码不触发。
---

# RN 审查规范

文中用代码标出的公共主题路径从 `$unif-platform-rules` 读取。

按 `uni-rn-dev` 核对受影响的 React／Hooks、组件和原生接线；涉及库工程、公开产物或独立消费时选用 `uni-rn-library`。本技能补充 Unif 项目契约与实际消费者的审查依据。

## 按变化读取

| 本次变化 | 本技能资料与工程依据 |
|---|---|
| 方案前提、已确认的范围与取舍、职责及场景交接 | 设计依据（`references/architecture/scope.md#11-设计依据与适用范围`）、职责（`references/architecture/responsibilities.md`）、调用与组合（`references/architecture/composition.md`） |
| 状态、身份、异步收尾和资源 | 状态归属（`references/architecture/state.md`）；Portal 同时核对[可订阅状态采用](../unif-rn-dev/references/rn/scope.md#21-可订阅状态) |
| 公共输入输出、协议与业务结果 | 交接契约（`references/architecture/contracts.md`） |
| 协议、字段或持久化实现退役 | `$unif-platform-rules` 的“契约变更与清理”，核对生成物、跨仓读写与 Portal 本地恢复 |
| 测试证据、消费者与回归范围 | 测试责任（`references/architecture/verification.md#72-测试责任`）、变更影响（`references/architecture/verification.md#73-变更影响`） |
| 外部调用、校验转换、失败抑制和恢复路径的诊断 | 日志与故障诊断（`references/architecture/verification.md#721-日志与故障诊断`） |
| Portal 环境文件复用、构建选择与加载一致性 | [文件规则](../unif-rn-dev/references/rn/file-rules.md)、[验证](../unif-rn-dev/references/rn/testing.md) |
| Portal 文件、公开入口与代码归属 | [范围](../unif-rn-dev/references/rn/scope.md)、[文件](../unif-rn-dev/references/rn/file-rules.md)；归属不清时补[目录](../unif-rn-dev/references/rn/directory.md)与[配置](../unif-rn-dev/references/rn/utilities-config.md) |
| Portal 组件、样式与公共能力组合 | [UI](../unif-rn-dev/references/rn/ui.md)、[依赖](../unif-rn-dev/references/rn/dependencies.md) |
| Portal 消费者、宿主与平台接线 | [验证](../unif-rn-dev/references/rn/testing.md)，按涉及接线补[依赖](../unif-rn-dev/references/rn/dependencies.md) |
| @unif RN 库与共享核心 | [RN 项目采用](../unif-rn-dev/references/rn/project.md)、本库公开契约与采用记录；共同规则按上表选读 |

发现项写明位置、触发条件、可观察影响及契约依据。共享源码同时核对受影响的 iOS、Android 或 Web 产物与消费者。
