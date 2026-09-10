# Portal 开发技能验证

## 固定材料与方法

spec 由架构项目的 `docs/specs/2026-09-10-portal-development-skill.md` 维护，本记录不复制或替代它。三份规则读取当前工作区文件，源摘要及冻结材料见 [manifest.json](manifest.json)。

三个代码场景先使用规则源作基线，再使用同一内容的生成快照与技能入口，各一次独立运行；另一次只给技能描述和入口约定，检查八类请求的选择。使用 `collaboration.spawn_agent`、`fork_turns: none`，各次不继承父任务对话；仅允许题设与指定材料，不向被测上下文提供 rubric、预期答案或其他产出。模型继承主任务默认设置，工具未提供精确模型版本、Token 或模型延迟。

主任务按[冻结判据](inputs/rubric.md)逐段人工核对文件位置、代码、状态与实际副作用。未运行题设 TS/TSX、SDK 或目标工程的编译测试；下面判断只针对书面产出。

## 行为结果

| 判据 | 仅规范基线 | 带技能 | 关键证据 |
|---|---|---|---|
| C1：共用组件与角色文件 | 满足 | 满足 | 两组都复用 CellList，将 props/条目接口、EMPTY_MESSAGE、主题样式放入所属 types/constants/styles，颜色与派生列表留组件，并删除无用 ref。 |
| C2：范围与公开出口 | 满足 | 满足 | 都未新增 BaseButton、业务 store/请求、空 Schema/变量文件或全平台 barrel；单元只公开组件及真实需要的类型。 |
| C3：UI 消费者与宿主 | 满足 | 满足 | 都列出中文空态、选择回调、主题切换、订单和聊天组合，并单列 Web 预览；不把原生测试当 Web 接入证据。 |
| D1：类型、固定值和调用资源 | 满足 | 满足 | 两组保持 pickImage 双参数形式，类型在 types.ts、DEFAULT_LIMIT 在 constants.ts；AbortController、Map、limit、files 留在每次调用中。 |
| D2：设备真实依赖与变化范围 | 满足 | 满足 | 都保留 bootstrap 正向注入，不反向读 app，不发明 Web 成功替身；验证三个实际消费者、并发隔离及原有取消传播，未来宿主变化再扩大平台验证。 |
| D3：领域适配与写入边界 | 满足 | 满足 | 两组均在所属适配器解释数值 200，保留缺名和 null 行的顺序，真实空数组与无列表数据分开；不默认选原因、补 ID 或读取后保存。 |
| D4：定向语义验证 | 满足 | 满足 | 都要求真实映射、可替换网络，断言码类型、列表字段、无写入与原因选择交接，不仅依赖类型检查或启动全部能力。 |
| U1：Schema 单一源 | 满足 | 满足 | 两组 types.ts 都使用 `z.infer<typeof orderInputSchema>`，不重复手写字段或为其他单元新装框架。 |
| U2：小工具与增长批次 | 满足 | 满足 | 仅补样本时保留 trimLabel.ts；出现显式选项和已有上限的另一批次才形成单元目录，私有辅助不单独建目录。未提供的选项字段和字符语义均标为缺口。 |
| U3：hook 生命周期 | 满足 | 满足 | 两组均保留实例 client、pending 与当前输入的作用域，只将固定 MODE_LABELS 移到所属常量文件；没有新状态、持久化或 variables.ts。 |
| U4：配置、声明与生成例外 | 满足 | 满足 | 都保留 env.ts、assets.d.ts、schema.generated.ts 的工具角色；生成改源，公开变化追踪消费者和语义，不以 any 或私有类型路径绕过边界。 |
| T1：八类请求选择 | 不作组间比较 | 满足 | 1/2/3 选择 portal-development，4 选择 architecture-design，5/6/7 不套客户端规则，8 两者并用；明确技能选择不证明静态门禁已经启用。 |

完整输出：

| 场景 | 基线 | 带技能 |
|---|---|---|
| 共用组件 | [control-component](outputs/control-component.md) | [skill-component](outputs/skill-component.md) |
| 设备与领域适配 | [control-capability](outputs/control-capability.md) | [skill-capability](outputs/skill-capability.md) |
| Schema、工具与应用文件 | [control-schema-utils](outputs/control-schema-utils.md) | [skill-schema-utils](outputs/skill-schema-utils.md) |
| 描述选择 | — | [discovery](outputs/discovery.md) |

基线已有正确表现，本次没有观察到技能相对基线的准确性改善。技能入口的价值在于明确触发和按类别组织资料，不能据此宣称已测得 Token 或时间收益。

## 机械验证与边界

- 现有同步脚本新增 portal-development 模式：三源先读取、统一生成，来源逐文件记录；默认 architecture-design 模式兼容。相关同步测试 9/9 通过，覆盖旧模式、三源内容及摘要、源变化、快照手改、记录损坏，以及缺源时不部分写入。
- 全部脚本测试 29/29 通过；技能参考校验和 quick_validate 通过，仓库校验发现两个技能并检查评测摘要。
- 五个文件的完整技能目录在含空格路径独立搬移后可验证；其 Markdown 引用均在自身目录内。无需依赖另一个已安装技能的私有文件。
- 规范同步 `--check` 通过；生成快照未手改。架构项目的 spec 和三份源文件、现有 architecture-design 文件、既有评测、插件配置及发布版本保持不变。
- 目标工程 AGENTS.md 入口及静态接入说明由 [接入文档](../../../../docs/portal-development-integration.md) 提供。当前实现的是技能仓的格式、引用、同步工具和评测完整性检查，未修改实际 Portal，也没有启用其 AST/ESLint 文件角色或依赖门禁。

仅七次独立书面运行，每个代码场景每组一次；未测真实宿主自动发现或强制调用、TS/TSX 编译、实际 SDK/设备、Portal CI 或业务联调。片段中的假设与缺口不能充当真实 API。未安装、提交、推送或发布本次技能。
