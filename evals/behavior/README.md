# CI 自包含行为题库

本目录为 Unif Portal Dev Skills 的只读 CI 输入，覆盖本包 22 个技能的发现与资料应用。它补充现有评测，不替代原始题目、人工判据、冻结源码清单或历史记录。

## 本次选题范围

默认 `scope=affected`，按固定基线与候选的实际变化选题；`scope=all` 明确选择整份题库。选题范围与重复模式独立，`full` 不再隐含全库评测。

- 技能源与分包内的同名生成副本映射到同一技能，只评一次。单纯版本字段或来源摘要、行段记录变化不扩大模型评测范围，分发一致性仍由仓库校验负责。
- 技能正文与配套资料变化选择该技能的题目；名称、触发描述或可见技能集合变化，再覆盖明确声明的跨技能发现约束。其他技能的发现题只读取目录元数据，不因无关正文变化重跑。
- 插件元数据或市场映射变化按受影响包的成员选题；题库内容变化定位到变动题目。共用评测器或其工作流变化覆盖全库，普通 CI、历史资料或生成脚本变化本身不启动全库模型调用。
- 摘要记录本次范围与实际覆盖数量；未选技能标为未评测，不将其计作失败，也不声称本次覆盖全库。已选题缺样本、执行错误与统计证据不足仍如实保留。

## 覆盖与执行边界

| 来源组 | 应用 | 正例 | 反例 | 合计 |
| --- | ---: | ---: | ---: | ---: |
| 架构、交付及 RN/鸿蒙/Python 开发、测试、审查 | 11 | 11 | 11 | 33 |
| 11 个库能力技能 | 11 | 11 | 11 | 33 |
| 原生库补充：Icons、Design、Chat、Camera、HMS Scan、Umeng、Logger | 7 | 0 | 0 | 7 |
| 已有能力复用与任务接续 | 1 | 0 | 0 | 1 |
| Python 智能体、领域能力与类型检查 | 3 | 0 | 0 | 3 |
| 合计 | 33 | 22 | 22 | 77 |

每技能至少有一项应用、发现正例和发现反例。流程题沿用 `<skill>-<mode>`；库题保留 `app-unif-*`、`pos-unif-*`、`neg-unif-*`、`native-unif-*` 的稳定题号。

应用模式只提供目标技能的一个完整目录、固定题面和题内 fixtures；配套文件随该目录提供，不依赖兄弟技能、其他私有仓库、本机安装位置、外部凭据或真实业务服务。资料中的代码、diff、合成事件和记录是只读评测材料，不是可构建工程或实际运行结果。

发现模式只给本包 name/description、自然请求和必要题内事实，不给技能正文。只评价 `required_skills` 与 `forbidden_skills` 的本包约束；跨包要求已移除，未列约束的选择不按数量机械惩罚。纯接口查询的库正例明确排除开发、测试、变更审查、架构与交付误触发；阶段正反例按原任务范围评价，不因提到“测试绿色”或“CI 状态”自动进入其他阶段。本包反例通过不证明外包替代技能被正确发现。

## 来源与适配

| CI 素材 | 原有依据 | 适配方式 |
| --- | --- | --- |
| 11 个流程技能的 33 题 | [独立技能题](../independent-skills/cases.md)、对应 RN/Python/鸿蒙行为与触发题，以及架构/交付题；各题 `source` 精确定位 | 依据对应原题适配为 CI 匿名 fixtures，保留契约、代码场景与语义判据；发现集合限定本包 |
| Design、Chat、Icons、Camera、HMS Scan、Umeng | [库能力 A–F 与发现题](../library-skills/cases.md)、[冻结来源](../independent-skills/capability-fixtures.json) | 采用固定修订的必要文档/公开入口节选，加匿名消费草案；不复制全库源码 |
| AMap、Files、Logger、OSS、Speech | [K1–K5](../library-skills/additional-library-cases.md)、[来源清单](../library-skills/additional-library-fixtures.json) | 将完整 example/实现追踪收窄为资料应用；保留取消、回执、身份、文件/设备释放的判断 |
| 原生六库 | [HN1–HN6](../library-skills/harmony-library-cases.md)、[来源清单](../library-skills/harmony-library-fixtures.json) | 提供必要包入口、状态、公开参数或目标规范节选；保持冻结版本实际能力 |
| 原生 Logger | [K6](../library-skills/additional-library-cases.md)、[来源清单](../library-skills/additional-library-fixtures.json) | 保留完整小型公开入口、Files、来源锁定与 example 节选，对照 RN 新导出 |
| 已有能力复用与任务接续 | `unif-architecture-design-existing-capability` 的匿名合成源码与确认记录 | 沿实际入口判断现有能力与接线缺口，保留实例和资源责任，避免重复实现及重新引入已撤回要求 |
| Python 目录与类型检查 | [助手接入专项 A–C](../independent-skills/assistant-integration-cases.md)、[对应判据](../independent-skills/assistant-integration-rubric.md) | 覆盖顶层 agent、独立 capabilities、普通接口和通用 memory 消费者，以及目标工程 BasedPyright 要求 |

库题依据上表对应原题适配，包含 22 项发现题和 18 项应用题。每题 `source` 指向原题编号与适配说明；实际引用的 Git 修订、来源文件/行、整文件 SHA-256 与节选 SHA-256 内嵌在 `reference/provenance.json`。`whole-file` 只用于必要的小型入口/参数文件，`contiguous-excerpt` 和 `selected-lines` 明示节选；CI 使用题内资料，不通过网络补全来源。

合成草案与事件写在 `scenario.md`、`proposal.md`、`events.md` 等文件，刻意与真实来源节选区分。它们用于把文档契约应用到具体决策，不冒充生产调用或执行日志。真实 API 名称来自固定资料；缺失能力、接口或验证仍明确缺失。

固定原生 Design、Chat、Camera、HMS Scan、Umeng 的版本为 `0.0.0`，公开入口只有 `export {};`，工程开发保持暂停；目标规范不能充当已实现 API。Icons `0.5.5` 有真实原生出口。Logger `0.1.3` 的来源锁定 RN `ca8bda0d279a1ec07016a0feb6355c890cd7a3cc`，不能假定 RN `0.2.0` 新接口已同步。这些是题内固定修订的状态，不声明源仓最新状态。

## 格式与判分

`cases.json` 根为 `formatVersion: 1` 与 `cases`。每题含 `id`、`skill`、`mode`、`prompt`、`fixtures`、`rubric`、`required_skills`、`forbidden_skills`、`source`。`mode` 仅为 `application`、`discovery_positive`、`discovery_negative`；fixture 键是相对路径，运行时位于 `fixtures/`，应用技能位于 `skills/<skill>/`。

应用 `rubric` 不交给作答模型，由独立模型上下文逐项评阅回答与读取轨迹并保留理由，结果需人工抽查。判据要求指出具体调用、状态与数据影响、交错顺序、真实消费者和证据限制；不能仅以关键词命中或复述规则判分。发现评分只使用本包集合约束。

题库更新需同时核对题面/资料/判据是否自洽、引用修订与摘要是否一致、ID/路径是否有效、每技能三类覆盖是否齐全。若实际来源契约与原判据冲突，应记录适配原因并保留原专项历史，不能为通过而把错误行为改成要求。候选与基线必须用同一题库、模型和判据，不混合不同来源版本的分数。

## 仍由专项评测覆盖的内容

本 CI 只迁移自包含资料应用与单包发现。完整真实源码的消费者追踪、实施与回归测试仍使用原题及其冻结 `project_sources`；本目录没有把 K1–K6 的完整 example/控制器/原生依赖复制进来。现有库题 G/H/I、Icons 双端生成 J1/J2 的实际操作、不同 Design 版本的原按钮行为、Chat 手势与设备交错等专项并未由这些改写题替代。

实际宿主自动发现/加载、独立包/HAR 消费、构建、真机权限与 UI、录音/定位/扫码/分享/上传、文件实际读取与释放、发布后安装以及真实业务验收仍需单独证据。题库结构有效、模型正确答题、源码存在或空 HAR 构建都不能替代这些层级。未执行、缺配置、请求失败或材料不足按证据不足处理；不把模型评阅当设备验收。
