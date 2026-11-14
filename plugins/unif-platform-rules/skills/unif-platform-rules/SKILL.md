---
name: unif-platform-rules
description: 查阅 Unif 项目共用的职责、状态、业务回执与验证规则时使用。其他 Unif 技能引用本目录的具体主题时，按给出的路径和章节读取。
---

# Unif 平台规范

按任务选读主题。业务技能给出 `references/…` 路径时，从本技能的位置打开对应文件，有章节名时直接定位到该节。工程指定了规范修订时，使用工程采用的修订。

| 涉及的工作 | 规范入口 |
|---|---|
| 设计范围、系统职责与场景交接 | [设计依据](references/architecture/scope.md)、[职责](references/architecture/responsibilities.md)、[场景组合](references/architecture/composition.md) |
| 草稿与执行状态、跨系统输入输出、订单等业务回执 | [状态归属](references/architecture/state.md)、[交接契约](references/architecture/contracts.md#63-取消失败与未确认结果) |
| 引入依赖、验证实际消费者 | [验证范围](references/architecture/verification.md) |

订单、拜访等领域的详细规则沿主题内链接进入所属专项文档。规范仓相对路径以工程采用的 [Unif 平台架构仓](https://github.com/unif-design/unif-platform-architecture) 为根。
