---
name: unif-harmony-dev
description: 在 Unif 原生鸿蒙 ArkTS／ArkUI 客户端、@unif/harmony-* HAR 库或其共享核心中实现、调整或排查源码和运行示例时使用。仅查询版本或既有 API、纯文档维护及 RN 开发不触发。
---

# Unif 鸿蒙代码开发规范

本目录提供 Unif 原生鸿蒙项目约定，不重复定义平台通用规则，独立使用不要求安装其他技能。先确定应用消费、HAR 库维护或共享核心，再按当前单元、契约与消费者取得实现依据。

## 依据

优先采用任务或工程指定且当前有效的规则版本；同一上下文已读且覆盖当前判断的内容直接复用。按本次任务选读，不因工作区包含 RN 或后端而扩大修改。具体 ArkTS／ArkUI API、SDK 版本、工具与命令从目标工程采用资料取得。

持久化、恢复、跨设备同步、业务记录创建，或异步处理、状态交接、资源收尾：读取[状态归属](references/common/state.md)，核对权威来源、唯一性、执行归属及对应验证；取得共同规则不重启架构设计。

涉及外部依赖、持久化、异常转换、异步收尾、降级或恢复时，同时读取[验证与故障诊断](references/common/verification.md#721-日志与故障诊断)，核对本次调用链的记录责任及对应测试。

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

应用按业务职责组合，HAR 按自身能力组织。比较 RN 行为可读取对应资料，但不能据此调用 RN API。共同功能按同一契约与案例核对两端真实消费者，源修订、产物及运行证据分别登记。

公共名称、输入输出、取消和业务成功按[交接契约](references/common/contracts.md)及所属模块契约核对。需要实质调整职责、调用或状态归属时先取得相应设计依据；按已有契约实现、排查或整理时不重启设计。实际业务契约缺失只限制依赖该缺口的工作。

领域、库及 SDK 契约按需从目标工程取得。专题中未另标所属仓库的规范路径相对于工程采用的 unif-platform-architecture 规范根目录；标明库根目录的路径按所属库定位。它们是外部依据入口，不表示完整契约随技能分发；未明确根目录时先从工程入口定位。生成的客户端主题溯源见 references/source.json，专项资料按所列契约与当前代码核对。

## 应用

确定本次单元及实际消费者。局部修改沿用仍有效的已确认行为；跨任务交接区分用户确认的范围与技术方案，并说明仍未解决的影响。新增自有适配先核实已有公开能力与实际缺口，再核对文件角色、公开出口、运行期归属、契约同源及实际接线。
