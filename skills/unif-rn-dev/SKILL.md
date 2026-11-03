---
name: unif-rn-dev
description: 在 Unif React Native 客户端、@unif/react-native-* 库或其共享核心中实现、调整或排查源码及运行示例，维护构建配置与环境变体，或进行 iOS 真机调试时使用。单纯版本、已有接口、文档维护或原生鸿蒙开发不触发。
---

# RN 代码开发规范

本技能维护 Unif RN 项目约定。先确定应用消费、库源码维护或共享核心，再按当前单元、契约与消费者取得实现依据。本目录携带开发必需的规范资料；按本次任务使用，不要求安装其他阶段或能力技能。

代码组织、RN 实现、库工程和文档遵循目标工程已采用的规范，从 AGENTS.md、开发说明和实际配置定位。纯文案任务按工程文档约定处理，不因此启动客户端开发。

## 依据

优先采用任务或工程指定的规则版本。同一上下文中已读、版本适用且覆盖当前判断的规则和契约直接复用；范围或来源变化时只补相关部分。以下资料按需选择，不因属于同一技能而全部加载。

目标由任务与实际工程确定，不因工作区同时包含多个平台而扩大修改。iOS、Android 与 Web 按本次实际影响核对；共享核心同时核对完整依赖及已采用目标的运行环境。

持久化、恢复、跨设备同步、业务记录创建，或异步处理、状态交接、资源收尾：读取[状态归属](references/common/state.md)，核对权威来源、唯一性、执行归属及对应验证；读取共同规则不重启架构设计。

涉及外部依赖、持久化、异常转换、异步收尾、降级或恢复时，同时读取[验证与故障诊断](references/common/verification.md#721-日志与故障诊断)，核对本次调用链的记录责任及对应测试。

React Native 的 Portal 项目约定：

- 通用文件规则的项目采用关系：[文件规则](references/rn/file-rules.md)。
- SDK 与公共能力选用、组件和样式复用：[复用规则](references/rn/ui.md)。
- Portal 存储、配置及资源的具体归属：[归属规则](references/rn/utilities-config.md)。
- 环境文件复用、构建选择与加载副本：[文件规则](references/rn/file-rules.md)、[验证](references/rn/testing.md)。
- 公共入口、依赖、基础能力与宿主接线：[依赖规则](references/rn/dependencies.md)。
- 任务范围、状态表定位与实现边界：[开发范围](references/rn/scope.md)。
- 初始化工程与代码归属：[目标目录](references/rn/directory.md)。
- 测试组织、质量、变更影响与交付证据：[测试与验收](references/rn/testing.md)。

库与专项接入：

- @unif RN 库的目标契约、文档框架与工程资料来源：[RN 项目采用](references/rn/project.md)。库创建、维护、验证与发布沿用本库已采用的规范和实际配置。
- RN 库的公开能力、接入与排障按下表从采用版本的公开文档取得；应用只消费公开 API 时不加载库维护流程。
- 文档站和运行示例按本库开发说明、构建配置与实际消费者维护。只改组件内部且不影响网站时不加载站点资料。
- 开发或排查 H5 容器、设备消息、文档与授权交接：[H5 桥接](references/rn/h5-bridge.md)。
- iOS 真机安装、Metro 热刷新或设备调试连接恢复：[真机调试](references/rn/ios-device-debugging.md)。仅需准备用户手测时也可读取；组件内部修改或版本查询不因此启动设备流程。

| 涉及的 React Native 库能力 | 公开资料入口 |
|---|---|
| 基础组件、主题、字体与 UI 宿主 | [Design](https://unif-design.github.io/react-native-design/llms.txt) |
| 消息、输入、附件和聊天组合 | [Chat](https://unif-design.github.io/react-native-chat/llms.txt) |
| 拍照、录像、水印和媒体交接 | [Camera](https://unif-design.github.io/react-native-camera/llms.txt) |
| 实时扫码、图片识别和手电 | [HMS Scan](https://unif-design.github.io/react-native-hms-scan/llms.txt) |
| 初始化、统计与第三方分享 | [Umeng](https://unif-design.github.io/react-native-umeng/llms.txt) |
| 图标消费、SVG 源与生成 | [Icons](https://unif-design.github.io/react-native-icons/llms.txt) |
| 地图选点、定位、地点查询与高德唤起 | [AMap](https://unif-design.github.io/react-native-amap/llms.txt) |
| 文件操作、下载、生命周期与本地资源 | [Files](https://unif-design.github.io/react-native-files/llms.txt) |
| 结构化日志、身份隔离与诊断快照 | [Logger](https://unif-design.github.io/react-native-logger/llms.txt) |
| 临时凭证、上传、转存与源文件释放 | [OSS](https://unif-design.github.io/react-native-oss/llms.txt) |
| 音频采集、实时识别与语音输入 | [Speech](https://unif-design.github.io/react-native-speech/llms.txt) |

这些入口对应 RN 包，不声明原生鸿蒙支持；官网版本与当前依赖不一致时，改用本库对应修订的文档与公开类型。组合任务只取得实际涉及的能力；已安装的库能力技能可辅助定位，不是前置依赖。

公共名称、输入输出、取消和业务成功按[交接契约](references/common/contracts.md)及所属模块契约核对。需要实质调整职责、调用或状态归属时先取得相应设计依据；按已有契约实现、排查或整理时不重启设计。实际业务契约缺失只限制依赖该缺口的工作。

领域、库及 SDK 契约按需从目标工程取得。专题中未另标所属仓库的规范路径相对于工程采用的 unif-platform-architecture 规范根目录；标明库根目录的路径按所属库定位。它们是外部依据入口，不表示完整契约随技能分发；未明确根目录时先从工程入口定位。生成的客户端主题溯源见 references/source.json，专项资料按所列契约与当前代码核对。

## 应用

确定本次单元及实际消费者。局部修改沿用仍有效的已确认行为；跨任务交接区分用户确认的范围与技术方案，并说明仍未解决的影响。新增自有适配先核实已有公开能力与实际缺口，再核对文件角色、公开出口、运行期归属、契约同源及实际接线。
