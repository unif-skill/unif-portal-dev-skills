---
name: unif-rn-test
description: 在为 Unif React Native 应用、@unif RN 库或共享核心设计、编写、执行或评估测试时使用，包括异步与资源边界、诊断证据及真实消费者。仅查看测试状态不触发。
---

# RN 测试规范

文中用代码标出的公共主题路径从 `$unif-platform-rules` 读取。

从受影响的 RN 组件、宿主或应用入口运行用例，采用工程锁定的库版本和平台配置。

## 按测试问题读取

| 本次问题 | 本技能资料与工程依据 |
|---|---|
| 真实对象、替身与覆盖证据 | 测试责任（`references/architecture/verification.md#72-测试责任`） |
| 失败、校验转换、降级恢复及诊断证据 | 日志与故障诊断（`references/architecture/verification.md#721-日志与故障诊断`） |
| 消费者与回归范围选择 | 变更影响（`references/architecture/verification.md#73-变更影响`） |
| 状态、持久化、恢复、身份与异步交接 | 状态归属（`references/architecture/state.md`） |
| 调用、准备、选择与确认 | 能力与场景（`references/architecture/composition.md`） |
| 协议输入、取消、业务成功及未确认结果 | 交接契约（`references/architecture/contracts.md`） |
| Portal 环境加载、测试组织及 UI 消费者 | [Portal 验证](../unif-rn-dev/references/rn/testing.md)、[Portal UI](../unif-rn-dev/references/rn/ui.md) |
| @unif RN 库与共享核心的测试 | 本库采用的测试配置、公开契约与实际消费者；共同规则按上表选读 |

记录运行的命令、修订和目标平台。共享逻辑用例、原生适配、组件在真实宿主中的交互和业务结果按各自证据报告。
