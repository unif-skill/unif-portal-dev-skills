---
name: unif-harmony-test
description: 在 Unif 原生鸿蒙客户端、@unif/harmony-* HAR 库或其共享核心中设计、编写、修正或执行测试，以及评估测试质量与验证范围时使用。
---

# Unif 鸿蒙测试规范

按当前契约和实际消费者选择验证范围。本目录包含测试必需的共同与鸿蒙规则，可独立使用，不要求安装开发或其他技能；优先采用工程指定且当前有效的修订，同一上下文已有依据直接复用。

## 按测试问题读取

按表中主题与章节选读，保留本次测试所需的完整契约。

| 本次问题 | 本技能资料 |
|---|---|
| 真实对象、替身与覆盖证据 | [测试责任](references/common/verification.md#72-测试责任) |
| 失败、降级、恢复及诊断断言 | [日志与故障诊断](references/common/verification.md#721-日志与故障诊断) |
| 消费者与回归范围选择 | [变更影响](references/common/verification.md#73-变更影响) |
| 状态、持久化、恢复、身份与异步交接 | [状态归属](references/common/state.md) |
| 调用、准备、选择与确认 | [能力与场景](references/common/composition.md) |
| 协议输入、取消、业务成功及未确认结果 | [交接契约](references/common/contracts.md) |
| 原生鸿蒙、HAR 与跨端产物 | [鸿蒙验证](references/harmony/testing.md)；按变化补[状态](references/harmony/state.md)、[UI](references/harmony/ui.md)或[原生接入](references/harmony/integration.md) |

只读取实际涉及的资料，不因取得共同规则进入其他阶段。库 API、业务模块契约、命令和设备条件从目标工程取得；原生鸿蒙的 ArkTS／ArkUI、HAR 产物、宿主与设备证据分别核对；RN 测试不能证明鸿蒙实现可用。

## 应用

运行真实被测实现，替换外部边界，覆盖返回、状态、消费者交接及不应发生的副作用。替身保留所采用依赖的接口、参数和必要前置；依赖真实行为决定的结果，另以实际实现核对。

失败、降级或恢复变化按诊断责任验证安全原因、关联、取消、迟到及日志自身失败，保留原业务控制。测试预期来自有效契约，不能通过复制实现、排除源码或弱化断言获得绿色结果。

报告实际修订、命令和覆盖范围，区分源码检查、替身测试、产物、设备和真实业务证据。资料溯源见 references/source.json；读取资料不授权修改无关实现或执行外部操作。
