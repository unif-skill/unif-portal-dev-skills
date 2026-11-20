---
name: unif-platform-rules
description: 查阅 Unif 项目共用的职责、状态、业务回执与验证规则时使用。其他 Unif 技能引用本目录的具体主题时，按给出的路径和章节读取。
---

# Unif 平台规范

按任务选读主题。业务技能给出 `references/…` 路径时，从本技能的位置打开对应文件，有章节名时直接定位到该节。工程指定了规范修订时，使用工程采用的修订；技能快照与该修订有差异时，以采用修订为准并记录待同步项。

| 涉及的工作 | 规范入口 |
|---|---|
| 设计范围、系统职责与场景交接 | [设计依据](references/architecture/scope.md)、[职责](references/architecture/responsibilities.md)、[场景组合](references/architecture/composition.md) |
| 草稿与执行状态、跨系统输入输出、订单等业务回执 | [状态归属](references/architecture/state.md)、[交接契约](references/architecture/contracts.md#63-取消失败与未确认结果) |
| 引入依赖、验证实际消费者 | [验证范围](references/architecture/verification.md) |

订单、拜访等领域的详细规则沿主题内链接进入所属专项文档。规范仓相对路径以工程采用的 [Unif 平台架构仓](https://github.com/unif-design/unif-platform-architecture) 为根。

## 契约变更与清理

变更范围、兼容取舍和通用清理方法选用 `uni-code-organization`；测试有效性及失效用例处理选用 `uni-test-design`。Unif 跨仓清理按实际涉及的链路核对以下入口：

- 从所属 `contracts` 源追到模型投影、Python 运行校验及 TypeScript／Go 产物，按工程采用的[跨工程契约交付](https://github.com/unif-design/unif-platform-architecture/blob/main/runtime/contract-delivery.md)重新生成，同步移除退役产物，不手改生成文件。
- 对照模型输入输出、Marketing 领域处理、Agent 转交与结果保存，以及 Portal 展示、编辑和本地恢复的实际读写。模型投影不包含某字段，不代表 Portal 编辑或恢复不再消费它；迁移有效消费者后，再清理协议及相关测试、文档。
- 涉及服务端表或列时，同时核对 `db` 建表源、部署 `sql`、生成入口与结构测试。新库初始化定义的清理和已有数据库中的表、列、历史数据处置分别说明；已有数据库操作按已确认的数据处置范围执行。

完成后按本次实际子范围和验证证据更新工程采用的状态表，状态判定与跨仓登记沿用表内规则。
