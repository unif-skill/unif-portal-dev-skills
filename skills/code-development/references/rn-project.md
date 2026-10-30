# RN 项目采用

本专题只维护 Unif RN 工程的采用关系。通用代码组织、RN 实现、库工程和文档分别使用 `code-organization`、`react-native-development`、`react-native-library`、`documentation`；未安装时从工程指定的同一规范源取得，不复制旧版通用正文。

## 项目与组织来源

Portal 的业务目录、组件选用、状态和接入按本插件对应项目专题及所属架构执行。库保留自身目录与构建约定，不套用 Portal 的 app/domains/capabilities 结构。Design 和 Chat 的目标契约分别为规范根的 `libraries/react-native-design.md`、`libraries/react-native-chat.md`，其他库从自己的开发资料取得契约；目标设计不证明发布包已具备接口。

@unif RN 库采用组织标准仓 `unif-design/.github`。优先使用任务或工程指定修订，未指定时核对默认分支的已提交标准，工作分支和未提交草稿单独识别。

| 当前需要 | 组织标准来源 |
|---|---|
| 新库接入与公开交付前置 | ONBOARDING.md |
| 工作树、发行与产物检查 | scripts/check-repo.sh、templates/scripts/check-library.cjs，按标准选择模式 |
| 共享文件、Agent 入口与 LLM 生成器同步 | docs/13-sync.md、templates/ 和对应同步脚本 |
| CI、远端设置及主分支保护 | docs/03-ci.md、docs/05-branch-protection.md、scripts/setup-repo.sh |
| 首次、常规与恢复发布 | docs/04-release.md、templates/workflows/release.yml |
| 从应用提取与 SDK 补丁交付 | docs/14-library-extraction.md |

具体脚本行为、发布绑定、检查名称和版本规则由组织来源维护。同步与远端配置按本次授权实施；成熟库的小改动复用有效采用依据，不重做新库接入。

## 文档与示例

正式 RN 库文档站采用 Docusaurus。品牌、导航与页面结构沿用本库，Web 调试页和原生 example 各有用途；文档内容、站点生成与构建使用 documentation，可运行原生示例由 react-native-library 负责。鸿蒙 HAR 使用原生规范，不套用 RN Web 或 iOS/Android 示例。

共享首页样式采用当前 `@unif/react-native-design/docs-home.css` 公开出口；主题、字体和 UI 宿主按 unif-design 的实际版本接入。共享 LLM 生成器从组织 templates/llms 同步，Chat 的 API 转换等专属部分由本库维护；不另建手工 API 副本。

仅改 README 时取得 ONBOARDING 的内容入口与 documentation 规范即可，不因此进入接入或发布。公开发行的 README、文档站和产物要求仍由组织标准定义，文档构建不代表网站已部署。
