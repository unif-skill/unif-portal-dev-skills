---
name: unif-harmony-dev
description: 在 Unif 原生鸿蒙 ArkTS／ArkUI 客户端、@unif/harmony-* HAR 库或其共享核心中实现、调整或排查源码和运行示例时使用。仅查询版本或既有 API、纯文档维护及 RN 开发不触发。
---

# Unif 鸿蒙代码开发规范

按应用、HAR 或共享核心核对原生消费者与已确认范围。只在新发现的接入事实会改变原取舍时再确认。

## 依据

具体 ArkTS／ArkUI API、SDK 和检查命令从目标工程采用的修订取得。

身份、持久化和异步资源交接见[状态归属](references/common/state.md)。

第三方库、框架或 SDK 的设计、接入、封装与排障，按[依赖治理](references/common/verification.md#71-依赖治理)核对官方依据与项目采用条件。涉及外部依赖、持久化、异常转换、异步收尾、降级或恢复时，同时读取[验证与故障诊断](references/common/verification.md#721-日志与故障诊断)，核对本次调用链的记录责任及对应测试。

原生 ArkTS／ArkUI 应用与 `@unif/harmony-*` HAR 库：

- 新建或确定范围：[鸿蒙适用范围](references/harmony/scope.md)；仅在初始化或核对归属时读[工程目录](references/harmony/directory.md)。
- 项目源码归属、六库公开导出、同源资料、库文档与真实 ArkUI 示例：[文件与公共入口](references/harmony/files.md)，按实际原生库和站点标准组织。
- 业务身份及六库状态与媒体交接：[状态与生命周期](references/harmony/state.md)。
- 组件、主题、字号与玻璃效果：[原生 UI](references/harmony/ui.md)。
- 设备、SDK、HTTP／SSE／H5 与共同契约：[原生接入](references/harmony/integration.md)。
- 六库、共同功能与业务消费者验收：[鸿蒙测试与验收](references/harmony/testing.md)。

原生六库按当前能力选读同源专题；应用消费核对采用版本的公开入口和宿主，HAR 维护同时核对库契约、实际消费者与产物，共享核心核对完整依赖和各目标运行环境：

| 原生目标库 | 规范入口 |
|---|---|
| @unif/harmony-icons | [图标同源生成、公开入口与消费](references/harmony/icons.md) |
| @unif/harmony-design | [主题、字体、玻璃与 UI 宿主](references/harmony/design.md) |
| @unif/harmony-chat | [消息、输入、附件与受控交接](references/harmony/chat.md) |
| @unif/harmony-camera | [拍摄、选用、取消与媒体所有权](references/harmony/camera.md) |
| @unif/harmony-hms-scan | [识别、图片借用与结果交付](references/harmony/hms-scan.md) |
| @unif/harmony-umeng | [同意后初始化、统计与真实分享回执](references/harmony/umeng.md) |

这些规范定义 Unif 目标行为和验收，不证明已有原生包或导出。具体 API 从当前原生库公开源码、文档及目标 SDK 取得；没有出口时明确待实现，不把 RN 示例改包名充当 ArkUI 用法。提供方与协议采用按原生接入专题执行，平台示例不改变项目选型。

原生 Logger 的现有 API、`Files` 入口与 HAR 消费见 [harmony-logger 包文档](https://github.com/unif-design/harmony-logger/blob/main/library/README.md)。维护共享核心时核对该库 logger-source.json 的固定 RN 修订及生成器；采用版本、OHPM 发布和实际设备证据分别确认。已安装 unif-logger 时可按任务读取其鸿蒙资料，不是本技能的前置依赖。

对涉及多端的接口，按[交接契约](references/common/contracts.md)核对公共语义和各端消费者。规范路径从采用的架构仓定位，库路径从实际库根定位。

替换原生能力前查明现有 HAR 出口和实际调用方。迁移资源交接及宿主接线后，清理已失效且无消费者的实现。
