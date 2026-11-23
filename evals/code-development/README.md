# 客户端开发技能评测

本目录用合成工程检验代码组织、契约来源、依赖和消费者判断。RN 和原生鸿蒙分别使用 `unif-rn-project`、`unif-harmony-project` 核对项目采用。实现、测试和审查沿用原题的业务判据。

## 选择样本

| 评测对象 | 要观察的判断 |
|---|---|
| [单元组织](cases/unit-boundaries.md) | 新页面如何拆分，哪些代码应共享，已有计划和绿色检查能否证明当前文件组织合适。 |
| [SDK 选型](cases/sdk-choice.md) | 先核对已采用的公开能力及具体缺口，再判断是否需要自有适配。按题内事实评价选型理由。 |
| [复用与输入契约](cases/reuse-contracts.md)、[状态与范围](cases/status-scope.md)、[测试迁移](../code-testing/cases/test-migration.md) | 核对重构前后的输入拒绝、运行校验、资源生命周期和消费者保护。规范登记滞后或部分设计未定时，写清哪些工作仍可完成。 |
| [库与 H5](cases/platform-units.md) | 区分应用接入和库维护。检查 Chat 的目标接口与发布证据、Design 字体与组件范围、H5 文档及授权交接。 |
| [文档站](cases/documentation-site.md)、[README 内容分工](cases/readme-documentation.md) | 确定正式 Web 示例的站点路由、版本接线和详细接入资料位置。用组件内部样式、原生修复及成熟库文档维护作为范围对照。 |
| [新库与首次发布](cases/library-onboarding.md) | 从固定的工程片段、配置和脚本判断脚手架、组织采用、实际接入、历史发布及共享 example 的消费者。模板问题、安装版本差异和基线已满足项分别记录。 |
| [任务路由](cases/task-routing.md)、[上下文复用](cases/context-reuse.md)、[企业规则应用](cases/enterprise-rules.md) | 事实查询、排障、测试、审查、设计与交付选什么入口。连续追问时记录真正补读了什么，以及缺少规范时是否找到了所需依据。 |
| [局部范围与交接](cases/scope-handoff.md) | 只改呈现时保留已确认的交互；用户明确改变交互时落实新范围。检查交接能否区分用户决定和实施者的技术选择。 |
| [iOS 真机](cases/ios-device-debugging.md)、[图标公开入口](cases/platform-units.md#5-图标拆包后的公开入口) | iOS 题保留原入口对照，现行通用方法见 `uni-rn-dev`。核对指定设备、已有包和 Metro、WDA 恢复与手测授权，分别记录规范和专项入口的作用。 |
| [原生鸿蒙与 RN](harmony-cases.md)、[独立判据](harmony-rubric.md) | 核对应用／HAR、同源 TS 与资源、RN 局部修复、扫码回执、玻璃材质，以及身份与 H5 的交接。 |

## 运行与留证

1. 固定题目、工程事实、模型、工具条件和外部技能描述。题设里的方法名和路径只用于本题。代码样本先使用同一组规范作对照，再提供候选技能。规范与入口同时变化时，依次比较旧包、只更新规范和完整候选。[分组对照方法](../architecture-design/README.md#可重复执行方式)
2. 发现样本只提供实际可用的技能描述和工程入口约定。作答方只看到题目和材料。评阅方另读 `rubric.md`，按题面检查实际代码与语义，并核对工作入口、资料来源、真正读取的文件及重复读取记录。
3. 分别记录资料可达性、书面作答、宿主加载、编译、SDK 和设备上实际运行的结果。题目声称已读、基线已满足或外部模板修复的内容各按原证据解释，未复现的现象注明条件。

`cases/`、`rubric.md` 和本说明随仓库维护。原始 inputs、outputs、日志及 manifest 摘要放入本地忽略的 `runs/`，保留当时的名称和证据。运行结束后用 `python scripts/validate_repository.py --include-evals` 核对档案摘要；默认分发包校验独立运行。

## 原生六库专项

[六库固定请求](harmony-library-cases.md)与[独立判据](harmony-library-rubric.md)覆盖 Icons／Design、拍照选用与取消、图片借用、厂商提供方及 RN 排除场景。先冻结已验证的 P0 候选，再冻结六库候选，分别在独立上下文作答。实际读取与回答留在对应的本地运行记录中。
