# RN 项目采用

从本库入口与采用记录取得目标契约和规范修订，按其要求组织代码、实现、库工程和文档。

## 项目与工程来源

Portal 的业务目录、组件选用、状态和接入按本技能所列 RN 专题及所属架构执行。库保留自身目录与构建约定，不套用 Portal 的 app/domains/capabilities 结构。Design 和 Chat 的目标契约分别为规范根的 `libraries/react-native-design.md`、`libraries/react-native-chat.md`，其他库从自己的开发资料取得契约；目标设计不证明发布包已具备接口。

工程规则从本库 AGENTS.md、开发说明及已提交的采用记录取得，按任务指定的修订核对。已接入交付检查的工程读取 `.github/delivery.json` 与 `.github/scripts/check-delivery.cjs`；具体命令、检查范围和发布绑定以本库文件为准，不从其他工程推定。

| 当前需要 | 本库资料入口 |
|---|---|
| 新库接入、包身份与交付前置 | AGENTS.md、docs/DEVELOPMENT.md、package.json 与已采用的交付规范 |
| 检查、构建与产物 | package.json 的 scripts、实际检查脚本、打包配置和消费者记录 |
| CI、发布及主分支保护 | .github/workflows/、交付采用记录及本次核实的远端设置 |
| 文档、共享文件及生成器维护 | 文档构建配置、scripts/ 中的实际生成入口及其来源记录 |
| 从应用提取与 SDK 补丁交付 | 本次提取契约、宿主依赖／patches、库的原生接入说明 |

共享工具需要更新时，按采用记录定位维护源与适用修订。同步与远端配置按本次授权实施；成熟库的小改动复用有效采用依据，不重做新库接入。

## 文档与示例

正式 RN 库文档站采用 Docusaurus。品牌、导航与页面结构沿用本库，Web 调试页和原生 example 各有用途；内容、站点与运行示例按本库采用的文档规范和构建入口维护。鸿蒙 HAR 使用原生规范，不套用 RN Web 或 iOS/Android 示例。

共享首页样式采用当前 `@unif/react-native-design/docs-home.css` 公开出口；主题、字体和 UI 宿主按 @unif/react-native-design 的实际版本接入。LLM 文档使用本库已接入的生成器，更新时核对其采用来源；Chat 的 API 转换等专属部分由本库维护，不另建手工 API 副本。

仅改 README 时读取本库公开接口、接入资料及已采用的文档规范，不因此进入工程接入或发布。公开发行的 README、文档站和产物要求按本库已采用的交付规范核对；文档构建不代表网站已部署。
