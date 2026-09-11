---
name: architecture-design
description: 在 Unif Portal 及相关 Agent、Channel、CLI 工程进行架构与模块设计、能力契约审查，或分析职责、状态和公共契约的变更影响时使用。
---

# 架构与模块设计

在当前设计或审查中应用企业架构规范，以已确认需求、模块契约和实际消费者为依据。

## 依据

优先采用任务或工程指定的规范版本；未指定时按问题选读包内主题，已有依据足够时不扩读：

- 需求、范围与旧实现参考：[设计依据](references/scope.md)、[模块文档](references/documentation.md)。
- 调用、输入准备与结果复用：[能力、场景与入口](references/composition.md)；系统职责：[系统边界](references/responsibilities.md)。
- 状态与确认：[状态归属](references/state.md)、[入口确认](references/composition.md)。
- 自然语言任务与记忆：[智能体与上下文](references/agent-context.md)。
- 跨边界输入输出、业务成功、取消与未确认结果：[交接契约](references/contracts.md)。
- 测试、消费者与变更影响：[独立验证](references/verification.md)；调用与模型成本：[成本验证](references/cost.md)。

主题保留规范源文，溯源时读取 references/source.json。

模块契约确定公共名称与语义；未定部分标明草案及影响范围。资料缺口只限制依赖它的设计。

## 应用

按所选规范核对职责、交接、状态和验证范围，设计产物满足[最小验收依据](references/verification.md#74-设计交付的最小依据)。将企业要求用于当前工作流；已有契约覆盖的等价内部调整沿用有效设计，不重启讨论或另建一套设计模板。
