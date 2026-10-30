---
name: code-development
description: 在 Unif 的 RN／原生鸿蒙客户端、对应 @unif 库或共享核心中实现、调整或排查源码及运行示例，或进行 iOS 真机调试时使用。单纯版本、已有接口、文档或文档站内容维护不触发。
---

# 代码开发规范

本技能维护 Unif 项目约定。先确定目标平台及应用消费、库源码维护或共享核心，再按当前单元、契约与消费者取得实现依据。测试、审查和交付使用各自入口；它们可以按需取得本技能的工程规范，不因此启动开发工作。

通用代码组织使用 `code-organization`，RN 实现按需使用 `react-native-development`，库工程使用 `react-native-library`，文档编写使用 `documentation`；这些技能由独立 `uni-skills` 维护。纯文案任务直接使用文档入口，不因此启动客户端开发。

## 依据

优先采用任务或工程指定的规则版本。同一上下文中已读、版本适用且覆盖当前判断的规则和契约直接复用；范围或来源变化时只补相关部分。以下资料按需选择，不因属于同一技能而全部加载。

目标由任务与实际工程确定，不因工作区同时包含多个平台而扩大修改。RN 与原生鸿蒙共同功能对齐契约、资源和案例；各自使用框架适用的接口与工程组织。

持久化、恢复、跨设备同步、业务记录创建，或异步处理、状态交接、资源收尾：取得 architecture-design 的“状态归属”主题，核对权威来源、唯一性、执行归属及对应验证；读取共同规则不重启架构设计。

涉及外部依赖、持久化、异常转换、异步收尾、降级或恢复时，同时取得 architecture-design 的“独立验证”主题中的日志与故障诊断要求，核对本次调用链的记录责任及对应测试。

原生 ArkTS／ArkUI 应用与 `@unif/harmony-*` HAR 库：

- 新建或确定范围：[鸿蒙适用范围](references/harmony-scope.md)；仅在初始化或核对归属时读[工程目录](references/harmony-directory.md)。
- 实现、公开导出、纯 TS 与资源共享：[文件与公共入口](references/harmony-files.md)。
- UI 状态、Context、身份与资源收尾：[状态与生命周期](references/harmony-state.md)。
- 组件、主题、字号与玻璃效果：[原生 UI](references/harmony-ui.md)。
- 设备、SDK、HTTP／SSE／H5 与共同契约：[原生接入](references/harmony-integration.md)。
- 库文档与真实 ArkUI 示例：[公开入口与文档](references/harmony-files.md)，按实际原生库和站点标准组织。
- 测试、打包、宿主与设备证据：[鸿蒙测试与验收](references/harmony-testing.md)。

原生六库按当前能力选读同源专题；应用消费核对采用版本的公开入口和宿主，HAR 维护同时核对库契约、实际消费者与产物，共享核心核对完整依赖和各目标运行环境：

| 原生目标库 | 规范入口 |
|---|---|
| @unif/harmony-icons | [图标同源生成、公开入口与消费](references/harmony-icons.md) |
| @unif/harmony-design | [主题、字体、玻璃与 UI 宿主](references/harmony-design.md) |
| @unif/harmony-chat | [消息、输入、附件与受控交接](references/harmony-chat.md) |
| @unif/harmony-camera | [拍摄、选用、取消与媒体所有权](references/harmony-camera.md) |
| @unif/harmony-hms-scan | [识别、图片借用与结果交付](references/harmony-hms-scan.md) |
| @unif/harmony-umeng | [同意后初始化、统计与真实分享回执](references/harmony-umeng.md) |

这些规范定义目标行为和验收，不证明已有原生包或导出。具体 API 从当前原生库公开源码、文档及目标 SDK 取得；没有出口时明确待实现，不把 RN 示例改包名充当 ArkUI 用法。地图／POI 使用高德，统计与分享使用友盟，平台示例不改变提供方。外部技能按工程采用清单选读，不自动恢复归档项。

应用按业务职责组合，HAR 按自身能力组织。比较 RN 行为可读取对应资料，但不能据此调用 RN API。共享纯 TS 先检查完整依赖及运行环境，再按各采用目标验证产物和消费者；无框架导入或 Node 测试通过不证明通用兼容。资源与逻辑维护单一来源，不为零散函数新建泛化 utils。

React Native 的 Portal 项目约定（通用文件及实现规则从上述独立技能取得）：

- 通用文件规则的项目采用关系：[文件规则](references/file-rules.md)。
- SDK 与公共能力选用、组件和样式复用：[复用规则](references/ui.md)。
- Portal 存储、配置及资源的具体归属：[归属规则](references/utilities-config.md)。
- 公共入口、依赖、基础能力与宿主接线：[依赖规则](references/dependencies.md)。
- 任务范围、状态表定位与实现边界：[开发范围](references/scope.md)。
- 初始化工程与代码归属：[目标目录](references/directory.md)。
- 测试组织、质量、变更影响与交付证据：[测试与验收](references/testing.md)。

库与专项接入：

- @unif RN 库的组织标准、目标契约、文档框架与资料来源：[RN 项目采用](references/rn-project.md)。库创建、维护、验证与发布使用 `react-native-library`，不在本插件重复维护通用流程。
- RN 库的公开能力、接入与排障，按下表取得对应能力技能；应用只消费公开 API 时不加载库维护流程。
- 文档内容及文档站使用 `documentation`；可运行原生示例使用 `react-native-library`。只改组件内部且不影响网站时不加载站点专题。
- 开发或排查 H5 容器、设备消息、文档与授权交接：[H5 桥接](references/h5-bridge.md)。
- iOS 真机安装、Metro 热刷新或设备调试连接恢复：[真机调试](references/ios-device-debugging.md)。仅需准备用户手测时也可读取；组件内部修改或版本查询不因此启动设备流程。

| 涉及的 React Native 库能力 | 技能 |
|---|---|
| 基础组件、主题、字体与 UI 宿主 | unif-design |
| 消息、输入、附件和聊天组合 | unif-chat |
| 拍照、录像、水印和媒体交接 | unif-camera |
| 实时扫码、图片识别和手电 | unif-hms-scan |
| 初始化、统计与第三方分享 | unif-umeng |
| 图标消费、SVG 源与生成 | unif-icons |

这六个能力技能对应当前 RN 包，不声明原生鸿蒙支持。能力技能提供当前任务的资料入口与操作边界，项目约定由本技能提供，通用组织、RN 实现与库工程规则由相应独立技能提供。组合任务只取得实际涉及的能力；已明确接口的局部修改直接复用有效依据。单纯接口说明可直接使用能力技能，不因此进入开发阶段。能力技能未安装时从本库公开文档和工程指定规范取得同一依据，不因入口缺失自行安装或停止已具备依据的工作。

需要确定或实质调整模块职责、公共契约、调用交接或状态归属时，使用本插件 architecture-design。按已有契约实现、排查或整理时沿用有效设计；仅为核对已有规则，不重启架构设计。通用或项目技能未安装时，可从工程明确提供的同一规范源取得依据；缺少必需依据时明确影响，不用通用流程或旧工程惯例替代。

领域、库及 SDK 契约按需从目标工程取得。专题中未另标所属仓库的规范路径相对于工程采用的 unif-platform-architecture 规范根目录；标明组织标准仓或库根目录的路径按该仓定位。它们是外部依据入口，不表示完整契约随技能分发；未明确根目录时先从工程入口定位。生成的客户端主题溯源见 references/source.json，专项资料按所列契约与当前代码核对。

## 应用

确定本次单元及实际消费者。局部修改沿用仍有效的已确认行为；跨任务交接区分用户确认的范围与技术方案，并说明仍未解决的影响。新增自有适配先核实已有公开能力与实际缺口，再核对文件角色、公开出口、运行期归属、契约同源及实际接线。
