---
name: architecture-design
description: 在 Unif Portal 及相关 Agent、Channel、CLI 工程进行架构与模块设计、能力契约审查，或分析职责、状态和公共契约的变更影响时使用。
---

# 架构与模块设计

以已确认需求和目标模块契约为依据，从源码与消费者核实现状，形成可实现、组合和验证的设计。

## 依据

优先采用任务或工程指定的规范版本；未指定时按问题选读包内主题，已有依据足够时不扩读：

- 需求与范围：[设计依据](references/scope.md)、[模块文档](references/documentation.md)。
- 职责与调用：[系统边界](references/responsibilities.md)、[能力、场景与入口](references/composition.md)。
- 状态与确认：[状态归属](references/state.md)、[入口确认](references/composition.md)。
- 自然语言任务与记忆：[智能体与上下文](references/agent-context.md)。
- 跨边界输入输出、业务成功、取消与未确认结果：[交接契约](references/contracts.md)。
- 测试、消费者与变更影响：[独立验证](references/verification.md)；调用与模型成本：[成本验证](references/cost.md)。

主题保留规范源文，溯源时读取 references/source.json。

模块契约确定公共名称与语义；未定部分标明草案及影响范围。资料缺口只限制依赖它的设计。

## 设计与交付

围绕本次变化说明：

- **职责**：能力、场景、入口的分工，以及新增边界、状态或调用的实际需要与消费者。
- **交接**：各步骤的输入输出、实际路由、错误和副作用，前一步产出能否支持后一步。
- **状态**：草稿、确认和业务事实的归属，确认的有效范围及异步结果的接收责任。
- **验证**：真实被测单元、可替换的外部依赖、受影响消费者及扩大范围的条件。

文字、类型约束和验收保持一致，区分设计建议与已执行证据。已有契约覆盖的等价内部调整，沿用对应设计和有效验证。
