---
name: unif-platform-rules
description: 查阅 Unif 现行规则时使用，例如草稿归谁、停止等待后谁继续处理、哪个回执代表业务成功。要实施或审查已确定的跨仓字段变更时，选契约变更技能。
---

# Unif 平台规范

从工程指定的规范修订或随包主题读取与问题有关的章节。工程指定了修订时以该修订为准，记录影响本次判断的快照差异。

| 查询内容 | 规范入口 |
|---|---|
| 系统职责、设计范围、调用准备或用户确认 | [设计依据](references/architecture/scope.md)、[职责](references/architecture/responsibilities.md)、[场景组合](references/architecture/composition.md) |
| 业务身份、草稿、持久化和恢复 | [状态归属](references/architecture/state.md) |
| 交接、业务成功、取消等待与未确认结果 | [交接契约](references/architecture/contracts.md#63-取消失败与未确认结果) |
| 依赖、诊断责任、测试证据和实际消费者 | [验证范围](references/architecture/verification.md) |

其他技能通过 `$unif-platform-rules` 引用的 `references/…` 路径从本目录定位。按主题里的链接进入订单、拜访等专项契约；规范源相对路径从工程采用的[平台架构仓](https://github.com/unif-design/unif-platform-architecture)定位。实际跨仓字段替换、退役与旧数据迁移使用 `unif-contract-change`。
