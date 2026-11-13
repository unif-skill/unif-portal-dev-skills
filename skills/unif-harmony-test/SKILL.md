---
name: unif-harmony-test
description: 在 Unif 原生鸿蒙客户端、@unif/harmony-* HAR 库或其共享核心中设计、编写、修正或执行测试，以及评估测试质量与验证范围时使用。
---

# Unif 鸿蒙测试规范

按实际修订确定本次验证的是原生应用、HAR 消费者还是共享核心，再选择对应宿主。

设计行为用例、判断未覆盖分支或验收逐文件覆盖率时，可选用已安装的 `uni-test-design`。

## 按测试问题读取

| 本次问题 | 本技能资料 |
|---|---|
| 真实对象、替身与覆盖证据 | [测试责任](references/common/verification.md#72-测试责任) |
| 失败、降级、恢复及诊断断言 | [日志与故障诊断](references/common/verification.md#721-日志与故障诊断) |
| 消费者与回归范围选择 | [变更影响](references/common/verification.md#73-变更影响) |
| 状态、持久化、恢复、身份与异步交接 | [状态归属](references/common/state.md) |
| 调用、准备、选择与确认 | [能力与场景](references/common/composition.md) |
| 协议输入、取消、业务成功及未确认结果 | [交接契约](references/common/contracts.md) |
| 原生鸿蒙、HAR 与跨端产物 | [鸿蒙验证](references/harmony/testing.md)；按变化补[状态](references/harmony/state.md)、[UI](references/harmony/ui.md)或[原生接入](references/harmony/integration.md) |

按本次修订和运行命令说明 ArkTS／ArkUI 检查、HAR 实际导入、设备操作与业务结果分别覆盖了什么。
