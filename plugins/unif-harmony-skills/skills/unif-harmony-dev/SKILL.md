---
name: unif-harmony-dev
description: 在 Unif 原生鸿蒙 ArkTS／ArkUI 客户端、@unif/harmony-* HAR 库或其共享核心中实现、调整或排查源码和运行示例时使用。仅查询版本或既有 API、纯文档维护及 RN 开发不触发。
---

# Unif 鸿蒙代码开发规范

文中用代码标出的公共主题路径从 `$unif-platform-rules` 读取。

本技能维护 Unif 原生应用、HAR 与共享核心的项目采用、库契约和消费者验收。平台实现与库工程方法按下表选用，不复制到项目专题。

## 通用方法

| 工程事项 | 通用入口 |
|---|---|
| ArkTS／ArkUI、组件状态、Context、SDK 接入与宿主生命周期 | `uni-harmony-dev` |
| HAR 公共入口、依赖资源、打包发布与原生运行示例 | `uni-harmony-library`；应用仅调用已有 API 时不进入库工程流程 |
| 测试用例、替身、异常与并发场景、覆盖率判据 | `uni-test-design` |

按实际涉及事项组合；Unif 的目录、能力语义和验收对象由下列项目资料确定。

## 依据

身份、持久化和异步资源交接见状态归属（`references/architecture/state.md`）。

第三方库、框架或 SDK 的 Unif 采用条件按依赖治理（`references/architecture/verification.md#71-依赖治理`）核对。涉及外部依赖、持久化、异常转换、异步收尾、降级或恢复时，同时读取验证与故障诊断（`references/architecture/verification.md#721-日志与故障诊断`），核对受影响调用链的记录责任及对应测试。

原生 ArkTS／ArkUI 应用与 `@unif/harmony-*` HAR 库：

- 新建或确定范围：[鸿蒙适用范围](references/harmony/scope.md)；仅在初始化或核对归属时读[工程目录](references/harmony/directory.md)。
- 项目源码归属、六库公开导出、同源资料、库文档与真实 ArkUI 示例：[文件与公共入口](references/harmony/files.md)，按实际原生库和站点标准组织。
- 业务身份及六库状态与媒体交接：[状态与生命周期](references/harmony/state.md)。
- 组件、主题、字号与玻璃效果：[原生 UI](references/harmony/ui.md)。
- 设备、SDK、HTTP／SSE／H5 与共同契约：[原生接入](references/harmony/integration.md)。
- 六库、共同功能与业务消费者验收：[鸿蒙测试与验收](references/harmony/testing.md)。

原生六库按所需能力选读同源专题，核对采用版本的公开入口、Unif 库契约与实际应用消费者：

| 原生目标库 | 规范入口 |
|---|---|
| @unif/harmony-icons | [图标同源生成、公开入口与消费](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-icons.md) |
| @unif/harmony-design | [主题、字体、玻璃与 UI 宿主](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-design.md) |
| @unif/harmony-chat | [消息、输入、附件与受控交接](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-chat.md) |
| @unif/harmony-camera | [拍摄、选用、取消与媒体所有权](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-camera.md) |
| @unif/harmony-hms-scan | [识别、图片借用与结果交付](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-hms-scan.md) |
| @unif/harmony-umeng | [同意后初始化、统计与真实分享回执](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-umeng.md) |

这些规范定义 Unif 目标行为和验收，不证明已有原生包或导出。具体 API 从当前原生库公开源码、文档及目标 SDK 取得；没有出口时明确待实现，不把 RN 示例改包名充当 ArkUI 用法。提供方与协议采用按原生接入专题执行，平台示例不改变项目选型。

原生 Logger 的现有 API、`Files` 入口与 HAR 消费见 [harmony-logger 包文档](https://github.com/unif-design/harmony-logger/blob/main/library/README.md)。维护共享核心时核对该库 logger-source.json 的固定 RN 修订及生成器；采用版本、OHPM 发布和实际设备证据分别确认。

对涉及多端的接口，按交接契约（`references/architecture/contracts.md`）核对公共语义和各端消费者。规范路径从采用的架构仓定位，库路径从实际库根定位。

原生能力替换涉及 HAR 出口、资源交接及宿主接线；清理方法按 `uni-code-organization`，跨端契约退役按 `$unif-platform-rules` 的“契约变更与清理”核对。
