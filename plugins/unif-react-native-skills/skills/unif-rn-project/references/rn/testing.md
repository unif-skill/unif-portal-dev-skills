<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 ../source.json。 -->

## 5. 规则执行与定向验证

从工程 AGENTS.md 定位已采用的规范与状态表，按变更对象读取相关规则。维护工程入口时保留有效链接，不复制整份规范。

环境配置验证以本次选定的环境源为准：既有入口为本机 debug、测试 beta 和正式 prod，新增独立环境按有效契约核对。从原生构建入口核对 `ENVFILE` 选定的文件、实际加载值及受支持的显式覆盖。Portal 直接读取选定的环境文件，无需维护 `.env` 副本；iOS 不通过 `/tmp/envfile` 切换环境，指定文件缺失时禁止回退到 `.env`。核对完整变量和布局，不输出敏感值。结构检查通过不代替构建或进程实际加载。

静态约束由工程现有 TypeScript、ESLint 和检查脚本执行。文件调整除静态引用外，还核对 Portal 的路由、宿主、H5 协议与跨仓契约。

涉及外部依赖、持久化、异常转换、异步收尾、降级或恢复时，按[日志与故障诊断](https://github.com/unif-design/unif-platform-architecture/blob/main/ARCHITECTURE.md#721-日志与故障诊断)核对已有记录和本次失败路径。

测试质量遵循[平台测试责任](https://github.com/unif-design/unif-platform-architecture/blob/main/ARCHITECTURE.md#72-测试责任)，项目测试组织及平台接线见[工程组织第 6 节](testing.md#6-开发维护与定向验证)。系统合并与发布执行实际工程的完整门禁；证据对应当前提交、配置和执行层级。

## 6. 开发维护与定向验证

消费者迁移与清理、测试设计和 RN 宿主验证，按[文件开发规则中的任务入口](../../SKILL.md)选用对应技能。

Portal 测试按 `src` 的责任归属放在 `__tests__/`；项目消费者关系与业务验收按以下契约定位：

| 变化对象 | Portal 消费与验收 |
|---|---|
| Design／Chat 的应用接入 | Portal 验证自身组合、主题和宿主接线；库内部行为由所属库工程验证 |
| ScreenHeader、Sheet、图片预览与键盘组合 | 按对应组件契约核对原生导航、弹层、中文内容及场景操作 |
| capabilities 设备与本地能力 | 按本能力契约核对页面、对话及实际 H5 消费者的结果与资源交接 |
| integrations/h5 | 按消息协议核对原文档、授权、来源与结果映射，不以 SDK 调用完成冒充业务成功 |
| Agent 流与聊天展示 | 核对 integrations/agent 与 app/chat 的转换、展示及领域结果交接 |
| 账号、订单、拜访等场景 | 采用所属业务契约的身份、草稿、确认及恢复用例 |

系统合并与发布执行 Portal 工程配置的完整门禁。

单元维护依据其代码归属、契约、实现、直接依赖与对应测试。现状行为与目标职责对照、其他领域文档及模型评测仅在变更涉及相应内容时读取。目录和测试组织的收益在实际变更中按[平台架构第 8 节](https://github.com/unif-design/unif-platform-architecture/blob/main/ARCHITECTURE.md#8-成本与效果验证)测量。
