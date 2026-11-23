---
name: unif-architecture-design
description: 需要为 Unif 应用、服务或 @unif 库设计或评审模块职责、状态归属和公共接口时使用。跨仓字段已经定稿后，实施或审查该改动使用契约变更技能。
---

# Unif 架构与模块设计

从用户使用的页面、助手或公开接口开始，说明用户要完成什么、已有能力能完成哪部分，哪些职责或公开输入输出需要调整。按任务或工程指定的规范修订判断。

## 找到拥有状态和执行动作的一方

先沿现有调用找出谁准备输入、谁让用户选择或确认、谁能决定业务结果。两个入口要复用同一操作时，核实它们能否提供该操作需要的输入。已有操作会创建或提交数据时，要先确认这些副作用符合另一个入口的用途。公共规则见 `$unif-platform-rules` 的 `references/architecture/responsibilities.md` 和 `references/architecture/composition.md`。

状态会保存、恢复或跨模块交接时，明确接收方何时已经采用结果。发起方关闭页面后谁继续处理，取决于状态所有者和业务契约。跨端能力还要核对各自的原生出口和宿主。同一处公共规则中的 `references/architecture/state.md` 与 `references/architecture/contracts.md` 定义了这些边界。

涉及自然语言或多助手时，分别核对超级智能体的路由、助手协议和领域决策，确定各方实际需要的上下文。[智能体与上下文](references/architecture/agent-context.md)

## 让实现者能按设计验收

写清要保留的行为、改变它的依据、受影响的调用与资源，以及各消费者可以观察到的验收结果。依据和适用范围见 `$unif-platform-rules` 的 `references/architecture/scope.md#11-设计依据与适用范围`。需要换依赖或比较调用成本时，分别查看 `references/architecture/verification.md#71-依赖治理` 和[成本验证](references/architecture/cost.md)。

已知问题只影响某个入口时，标明该项还缺什么事实，并完成其余已有依据支持的决定。按 `references/architecture/verification.md#74-设计交付的最小依据` 和[领域文档要求](references/architecture/documentation.md)记录决定。跨仓字段形状已经确定后，用 `unif-contract-change` 实施或审查对应改动。
