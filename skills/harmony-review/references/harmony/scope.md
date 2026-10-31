<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 ../source.json。 -->

# Unif 原生鸿蒙开发规则

本文用于 Unif 的 ArkTS／ArkUI 应用、`@unif/harmony-*` 原生库及它们实际采用的共享源码。目录与 UI 归属见[鸿蒙工程组织](../../SKILL.md)，业务职责和验收沿用平台架构（规范源相对路径：`ARCHITECTURE.md`）及所属契约。React Native 工程使用 RN 文件规则（规范源相对路径：`PORTAL_DEVELOPMENT.md`），不能直接套用到原生鸿蒙。


## 1. 适用范围与实施

先确定本次目标为应用消费、库源码维护或共享核心，再选择对应平台规则。当前 Unif 原生目标是 HarmonyOS 7.0.0／API 26；执行时核对工程的 target／compatible SDK、实际 SDK、Hvigor、OHPM、设备和依赖版本。新目标或最低版本改变须来自明确任务，不自动增加低版本兼容或切换 RNOH。

开发前读取本次契约、已有公开能力和实际消费者。RN 是行为与资源参考，不把 TSX、Hooks、RN 样式、Zustand、Metro、Pods 或 RN 测试命令当作原生实现规则。业务登录仍采用既有账号、角色和设备校验；开发工具的华为账号不替代业务身份。

应用复用库的公开能力；库维护按自身职责、公开接口、示例与消费者组织，不套用 Portal 业务目录。六库对应关系为 `react-native-icons/design/chat/camera/hms-scan/umeng` 与同后缀的 `harmony-*`。这些是建设目标，不证明包已存在、能力齐全或已经发布。实际实现采用当前库的文档、导出与版本，不能从 RN 同名接口推导 ArkUI API。

| 本次工作 | 资料与实施边界 |
|---|---|
| 应用消费 | 所属场景契约、已采用原生库的版本／公开入口／接入说明和真实宿主；不为普通消费加载全库维护流程 |
| HAR 库维护 | 本库原生规范、对应 RN 行为契约、原生导出／SDK／文档、实际消费者及产物；原生 API 尚未形成时先实现并验证出口，不用目标名称冒充可用接口 |
| 共享核心或资源 | 单一来源、完整运行与类型依赖图、生成／打包方式及每个真实目标消费者；不得为零散函数新建泛化 utils 或两份手维副本 |

六库原生规范按本次能力选读：Icons（规范源相对路径：`libraries/harmony-icons.md#1-职责与依赖`）、Design（规范源相对路径：`libraries/harmony-design.md#1-职责与依赖`）、Chat（规范源相对路径：`libraries/harmony-chat.md#1-职责与依赖`）、Camera（规范源相对路径：`libraries/harmony-camera.md#1-职责与依赖`）、Scan（规范源相对路径：`libraries/harmony-hms-scan.md#1-职责与依赖`）、Umeng（规范源相对路径：`libraries/harmony-umeng.md#1-职责与依赖`）。它们维护职责、结果语义和验收，不复制完整 SDK 或全量 props；已实现 API 由所属库源码、公开文档与示例维护。RN 六库能力技能仍服务真实 RN 包。

新建库先核对已有能力与组织中适用的原生标准、包名及版本历史。工具模板只提供工程起点；建立真实的公开消费示例、打包与验证入口。首次版本按工程和包仓库规则确定，已有库不擅自升主版本；创建远端仓库、推送和发布分别按授权执行。

已明确的范围直接实施；未决 SDK、权限或业务差异只限制相应部分。规范、源码、包产物、安装和实际运行分别登记；不要求所有库齐全才推进已有消费者。
