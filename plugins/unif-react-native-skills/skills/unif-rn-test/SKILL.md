---
name: unif-rn-test
description: 在为 Unif React Native 应用、@unif RN 库或共享核心设计、编写、执行或评估测试时使用，包括异步与资源边界、诊断证据及真实消费者。仅查看测试状态不触发。
---

# RN 测试规范

文中用代码标出的公共主题路径从 `$unif-platform-rules` 读取。

通用用例设计与有效性采用 `uni-test-design`，RN 组件、Hook 与宿主验证采用 `uni-rn-dev`；涉及真实包产物、独立消费或原生示例时选用 `uni-rn-library`。本技能定位 Unif 的业务断言与消费者，使用工程锁定的库版本和平台配置。

## 按测试问题读取

| 本次问题 | 本技能资料与工程依据 |
|---|---|
| 真实对象、替身与覆盖证据 | 测试责任（`references/architecture/verification.md#72-测试责任`） |
| 失败、校验转换、降级恢复及诊断证据 | 日志与故障诊断（`references/architecture/verification.md#721-日志与故障诊断`） |
| 消费者与回归范围选择 | 变更影响（`references/architecture/verification.md#73-变更影响`） |
| 状态、持久化、恢复、身份与异步交接 | 状态归属（`references/architecture/state.md`）；Portal 状态接线按[可订阅状态采用](../unif-rn-dev/references/rn/scope.md#21-可订阅状态)核对 |
| 调用、准备、选择与确认 | 能力与场景（`references/architecture/composition.md`） |
| 协议输入、取消、业务成功及未确认结果 | 交接契约（`references/architecture/contracts.md`） |
| Portal 环境加载、测试组织及 UI 消费者 | [Portal 验证](../unif-rn-dev/references/rn/testing.md)、[Portal UI](../unif-rn-dev/references/rn/ui.md) |
| @unif RN 库与共享核心的测试 | [RN 项目采用](../unif-rn-dev/references/rn/project.md)、本库测试配置、公开契约与实际消费者；共同规则按上表选读 |

记录运行的命令、修订和目标平台。共享逻辑用例、原生适配、组件在真实宿主中的交互和业务结果按各自证据报告。
