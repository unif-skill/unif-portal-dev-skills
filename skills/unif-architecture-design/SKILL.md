---
name: unif-architecture-design
description: 在 Unif Portal、相关 Agent／Channel／CLI 及 @unif RN／原生鸿蒙库设计或评审模块职责、场景组合、状态归属和公共契约时使用。单纯查阅现有接口不触发架构设计。
---

# 架构与模块设计

先核对当前目标、候选方案的事实前提和实际消费者。涉及新的取舍时按[调整依据](references/scope.md#11-设计依据与适用范围)处理。

## 依据

优先采用任务或工程指定的规范版本；未指定时按问题选读包内主题。同一上下文中已读且仍适用的内容直接复用，只补新范围或新修订涉及的部分：

- 需求、范围与现有实现：[设计依据](references/scope.md)、[模块文档](references/documentation.md)。
- 调用、输入准备与结果复用：[能力、场景与入口](references/composition.md)；系统职责：[系统边界](references/responsibilities.md)。
- 状态、持久化、恢复、业务唯一性与异步交接：[状态归属](references/state.md)；交互确认：[入口确认](references/composition.md)。
- 自然语言任务与记忆：[智能体与上下文](references/agent-context.md)；多助手接入同时核对[系统边界](references/responsibilities.md)，区分超级智能体路由、助手协议适配和领域业务处理，目录按目标工程采用。
- 跨边界输入输出、业务成功、取消与未确认结果：[交接契约](references/contracts.md)。
- 第三方技术采用依据、依赖与复用：[依赖治理](references/verification.md#71-依赖治理)；测试与消费者：[测试责任](references/verification.md#72-测试责任)；回归选择：[变更影响](references/verification.md#73-变更影响)。
- 调用与模型成本：[成本验证](references/cost.md)。

模块契约确定公共名称与语义；RN／原生鸿蒙的应用、库与共享核心分别确认职责、消费者和运行边界，不以同名推定接口或实现兼容。平台组织与 SDK 约束从目标工程已采用的规范和当前配置取得，不要求另装开发技能。未定部分标明草案及影响范围。资料缺口只限制依赖它的设计。

## 应用

写明已有能力能否满足需要、新增或替换的依据，以及受影响的调用和资源如何迁移。

按所选规范核对职责、交接、状态和验证范围，设计产物满足[最小验收依据](references/verification.md#74-设计交付的最小依据)。已有契约覆盖的等价内部调整沿用有效设计，不重启设计或另建同义模板，也不以假设的新需求阻断这些工作。
