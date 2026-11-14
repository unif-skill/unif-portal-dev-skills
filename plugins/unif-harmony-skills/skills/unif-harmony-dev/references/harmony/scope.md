<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 ../source.json。 -->

# Unif 原生鸿蒙开发规则

开发 Unif 原生客户端、`@unif/harmony-*` 六库及共同功能时，先核对目标工程采用的 ArkTS／ArkUI、SDK 和 HAR 规范，再确认本次项目契约、已有能力及实际调用方。目录与 UI 职责分别见[工程目录](directory.md#1-工程目录与依赖)、[组件与材质](ui.md#2-组件主题与玻璃材质)，业务职责见[平台架构](https://github.com/unif-design/unif-platform-architecture/blob/main/ARCHITECTURE.md)及所属契约。


## 1. 适用范围与实施

Unif 原生产品目标为 HarmonyOS 7.0.0／API 26；新目标、最低版本变化或切换 RNOH 须来自明确任务。业务登录继续使用既有账号、角色与设备校验，开发工具的华为账号不替代业务身份。

本文“六库”指 `react-native-icons/design/chat/camera/hms-scan/umeng` 与同后缀的 `harmony-*`，用于界定下述规范范围，不是全部 Unif 原生库的清单。其他库入口见库索引（规范源相对路径：`libraries/README.md#原生鸿蒙库`），其中 Harmony Logger 按自身公开契约与固定 RN 来源维护。六库规范不代表原生包、导出或版本已经存在；RN 契约提供行为与资源对照，具体原生能力以所属库当前公开资料为准。

| 本次对象 | Unif 采用依据 |
|---|---|
| 应用消费 | 所属场景契约、采用的六库版本及应用接线 |
| 六库维护 | 本库原生规范、对应 RN 行为契约和实际应用消费者；未形成原生出口的能力登记为待实现 |
| 共同功能 | 共同契约、源头与实际 RN／鸿蒙消费者，登记各端修订和差异 |

六库规范按本次能力选读：[Icons](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-icons.md#1-职责与依赖)、[Design](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-design.md#1-职责与依赖)、[Chat](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-chat.md#1-职责与依赖)、[Camera](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-camera.md#1-职责与依赖)、[Scan](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-hms-scan.md#1-职责与依赖)、[Umeng](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-umeng.md#1-职责与依赖)。它们维护 Unif 的职责、公开结果语义与验收；各能力技能按自身范围提供 RN 用法与鸿蒙目标契约入口，实际原生 API 仍以采用库的公开出口为准。

是否进入产品实施以当前任务与状态登记为准；规范或技能发布不代表六库产品完成，也不要求所有库齐全才推进已授权消费者。
