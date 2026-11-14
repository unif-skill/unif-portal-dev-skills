---
name: unif-rn-dev
description: 在 Unif React Native 应用、@unif RN 库或共享核心实现、修复和重构源码、示例与构建配置，处理客户端状态、资源交接或故障诊断时使用。仅查 API／版本、纯文档及原生鸿蒙开发不触发。
---

# RN 代码开发规范

文中用代码标出的公共主题路径从 `$unif-platform-rules` 读取。

定位应用入口、所用 RN 库的公开能力和实际消费者。检查已同意的改法是否仍符合当前事实，发现新的实质影响时再请用户取舍。

修改兼容分支或异步保护需要设计回归时，按项目采用的通用测试规范执行。

## 依据

依据工程采用的修订，核对受影响的 iOS、Android 或 Web 接线。共享核心还须核对各目标的完整依赖。

身份、持久化和异步资源交接见状态归属（`references/architecture/state.md`）。

SDK 接入或排障按依赖治理（`references/architecture/verification.md#71-依赖治理`）核对采用版本。调用失败、数据转换或恢复路径按日志与故障诊断（`references/architecture/verification.md#721-日志与故障诊断`）核对真实记录，Logger API 以宿主采用的版本为准。

React Native 的 Portal 项目约定：

- 通用文件规则的项目采用、环境文件复用与构建选择：[文件规则](references/rn/file-rules.md)。
- SDK 与公共能力选用、组件和样式复用：[复用规则](references/rn/ui.md)。
- Portal 存储、配置及资源的具体归属：[归属规则](references/rn/utilities-config.md)。
- 公共入口、依赖、基础能力与宿主接线：[依赖规则](references/rn/dependencies.md)。
- 任务范围、状态表定位与实现边界：[开发范围](references/rn/scope.md)。
- 初始化工程与代码归属：[目标目录](references/rn/directory.md)。
- 环境加载、测试组织、质量、变更影响与交付证据：[测试与验收](references/rn/testing.md)。

库与专项接入：

- 核对 @unif RN 库的目标契约、工程资料，或判断缺陷应在原库、宿主还是第三方补丁中修复时，见 [RN 项目采用](references/rn/project.md)。库创建、维护、验证与发布沿用本库已采用的规范和实际配置。
- RN 库的公开能力、接入与排障按下表从采用版本的公开文档取得；应用只消费公开 API 时不加载库维护流程。
- 文档站和运行示例按本库开发说明、构建配置与实际消费者维护。只改组件内部且不影响网站时不加载站点资料。
- 开发或排查 H5 容器、设备消息、文档与授权交接：[H5 桥接](references/rn/h5-bridge.md)。

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

这些入口对应 RN 包，不声明原生鸿蒙支持；官网版本与当前依赖不一致时，改用本库对应修订的文档与公开类型。组合任务只取得实际涉及的能力。

跨模块的输入输出、取消与业务结果按交接契约（`references/architecture/contracts.md`）核对。

专题中未标库名的规范路径相对于工程采用的架构仓，库内路径从该库根目录定位。

## 应用

替换或撤销时，核对现有调用、状态写入和恢复，完成迁移再清理失效实现。保留兼容路径须有有效契约、消费者或数据保护依据。
