---
name: unif-harmony-review
description: 在 Unif 原生鸿蒙客户端、@unif/harmony-* HAR 库或其共享核心中对明确代码或工程配置变更进行缺陷、契约符合性和工程规范审查时使用。为回答事实问题而查阅源码不单独触发。
---

# Unif 鸿蒙审查规范

对照有效需求、契约、实际实现与消费者审查本次变化。本目录携带必需的共同与鸿蒙规范，不要求安装其他技能。独立审查需取得自身尚未具有的依据；同一上下文已读且仍适用的内容直接复用。

## 按变化读取

按表中主题与章节取得本次变化需要的依据。

| 本次变化 | 本技能资料 |
|---|---|
| 授权范围、职责与场景交接 | [设计依据](references/common/scope.md)、[职责](references/common/responsibilities.md)、[调用与组合](references/common/composition.md) |
| 状态、身份、异步收尾和资源 | [状态归属](references/common/state.md) |
| 公共输入输出、协议与业务结果 | [交接契约](references/common/contracts.md) |
| 测试证据、消费者与回归范围 | [测试责任](references/common/verification.md#72-测试责任)、[变更影响](references/common/verification.md#73-变更影响) |
| 新增或改变的失败路径 | [日志与故障诊断](references/common/verification.md#721-日志与故障诊断) |
| 原生工程、HAR 与公开入口 | [范围](references/harmony/scope.md)、[公开入口](references/harmony/files.md)；归属变化补[目录](references/harmony/directory.md) |
| 库状态、主题与布局 | [状态](references/harmony/state.md)、[UI](references/harmony/ui.md)，按实际变化选读 |
| 原生能力、协议与消费者 | [接入](references/harmony/integration.md)、[验证](references/harmony/testing.md) |

工程指定了规则修订时采用该修订。具体业务、库 API 与 SDK 契约从工程入口和实际公开资料取得，不把模板、评测样例或偏好当成新增需求。原生鸿蒙的 ArkTS／ArkUI、HAR 产物、宿主与设备证据分别核对；RN 测试不能证明鸿蒙实现可用。

## 输出

核对新增或改变的失败路径是否可诊断，原因是否在包装或抑制时丢失、敏感数据是否泄露，原权限、身份、取消、事务和资源保护是否有效。共享源码检查真实产物和消费者；单端验证不替代其他目标。

只报告有证据的问题，说明位置、触发条件、实际影响及对应契约。区分需要修复的实现缺陷与已授权设计变化；审查不自动授权修复、提交或发布评论。资料溯源见 references/source.json。
