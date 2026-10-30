# 工程技能入口

Unif 工程按任务组合通用规则、企业约定与能力资料，入口只引用名称和有效来源，不复制规则正文。仅安装单个库能力技能的项目继续使用自己的工程标准。

## 入口示例

```markdown
## 开发规范

- 目录、文件角色、命名与公开入口使用 code-organization；RN 组件、Hook、样式及平台实现使用 react-native-development。
- RN 库创建、维护、打包、发布及运行示例使用 react-native-library；各种文档和文档站使用 documentation。
- Unif 客户端和库的项目约定使用 code-development，按 RN／原生鸿蒙及应用／库／共享核心选取专题。Portal 业务目录、库所属契约与实际模板来源分别核对。
- 模块职责、公共契约、状态与场景组合使用 architecture-design；Python 后端实现使用 backend-development。
- 测试、明确代码变更审查、交付分别使用 code-testing、code-review、code-delivery，并取得本次所需的通用及项目依据。
- 具体库 API 按实际任务读取 unif-design、unif-chat、unif-camera、unif-hms-scan、unif-umeng 或 unif-icons；单纯接口查询不启动开发阶段。
- 同一上下文已读且仍有效的资料直接复用，读取规则不重新启动工作阶段。实际命令、门禁、发布方式及操作授权从当前工程和任务取得。
```

## 资料归属

通用四技能由独立 uni-skills 维护，每个可单独使用。采用工程应明确所需资料的可访问来源；本插件的客户端目录不再包含第二份通用正文。企业技能未安装但工程已提供同一规范源时，直接取得必要依据，不依赖作者路径或已失效的缓存。

code-development 的 Portal／鸿蒙主题由架构仓生成，RN 项目采用、H5 与真机操作资料在技能仓维护。规范源和客户端 spec 仍属于 unif-platform-architecture；状态表按本次相关条目读取，不随技能分发成固定状态。

新 @unif RN 库或首次／恢复发布，按 react-native-library 及“RN 项目采用”取得组织 .github 的已采用标准。成熟工程普通维护复用有效依据；库使用自己的构建和原生目录，不套 Portal 业务结构。单纯 README 修改使用 documentation，不启动工程接入。

原生鸿蒙应用、HAR 与共享核心使用 code-development 的原生专题和真实 ArkTS/ArkUI 工程依据。六库专题描述目标契约与验收，实际 API 以采用库导出及 SDK 为准；RN 六库能力技能不提供 ArkUI API。地图／POI、友盟等企业选型保留在原生契约中。

iOS 安装、Metro 和连接恢复仍使用真机调试专题，复用有效交接并区分 JS、原生构建、安装与实际运行。H5、身份、协议和资源保护按所属企业契约核对。

## 验证与分发

阶段入口定位所需规则，不另维护 TDD、审查编排或 Git 流程。目标项目用实际 TypeScript/ESLint、ArkTS/Hvigor 或后端工具落实适用检查；技能文本与格式校验不表示项目静态门禁已启用。

独立分发保留完整技能目录及必要引用。通用技能、企业规范、能力 API 和工具知识按本次目标取得，不自动安装未授权依赖或恢复归档技能。

技能格式、生成快照、模型应用、插件安装及真实工程检查分别验证。规范或技能维护完成不自动启动应用开发、提交、发布、安装或设备任务。
