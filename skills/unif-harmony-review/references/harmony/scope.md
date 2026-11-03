<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 ../source.json。 -->

# Unif 原生鸿蒙开发规则

本文只维护 Unif 原生客户端、`@unif/harmony-*` 六库及共同功能的项目约定。平台通用开发与 HAR 工程规则由所采用的通用标准维护，本文不另设语言、状态管理、SDK 用法或打包流程。各技能独立分发，不建立相互安装或调用依赖。目录与 UI 职责见[鸿蒙工程组织](../../SKILL.md)，业务职责见平台架构（规范源相对路径：`ARCHITECTURE.md`）及所属契约。


## 1. 适用范围与实施

Unif 原生产品目标为 HarmonyOS 7.0.0／API 26；新目标、最低版本变化或切换 RNOH 须来自明确任务。业务登录继续使用既有账号、角色与设备校验，开发工具的华为账号不替代业务身份。

本文“六库”指 `react-native-icons/design/chat/camera/hms-scan/umeng` 与同后缀的 `harmony-*`，用于界定下述规范范围，不是全部 Unif 原生库的清单。其他库入口见库索引（规范源相对路径：`libraries/README.md#原生鸿蒙库`），其中 Harmony Logger 按自身公开契约与固定 RN 来源维护。六库规范不代表原生包、导出或版本已经存在；RN 契约提供行为与资源对照，具体原生能力以所属库当前公开资料为准。

| 本次对象 | Unif 采用依据 |
|---|---|
| 应用消费 | 所属场景契约、采用的六库版本及应用接线 |
| 六库维护 | 本库原生规范、对应 RN 行为契约和实际应用消费者；未形成原生出口的能力登记为待实现 |
| 共同功能 | 共同契约、源头与实际 RN／鸿蒙消费者，登记各端修订和差异 |

六库规范按本次能力选读：Icons（规范源相对路径：`libraries/harmony-icons.md#1-职责与依赖`）、Design（规范源相对路径：`libraries/harmony-design.md#1-职责与依赖`）、Chat（规范源相对路径：`libraries/harmony-chat.md#1-职责与依赖`）、Camera（规范源相对路径：`libraries/harmony-camera.md#1-职责与依赖`）、Scan（规范源相对路径：`libraries/harmony-hms-scan.md#1-职责与依赖`）、Umeng（规范源相对路径：`libraries/harmony-umeng.md#1-职责与依赖`）。它们维护 Unif 的职责、公开结果语义与验收；RN 六库能力技能继续服务实际 RN 包。

是否进入产品实施以当前任务与状态登记为准；规范或技能发布不代表六库产品完成，也不要求所有库齐全才推进已授权消费者。
