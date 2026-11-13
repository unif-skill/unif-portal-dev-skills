---
name: unif-harmony-review
description: 在 Unif 原生鸿蒙客户端、@unif/harmony-* HAR 库或其共享核心中对明确代码或工程配置变更进行缺陷、契约符合性和工程规范审查时使用。为回答事实问题而查阅源码不单独触发。
---

# Unif 鸿蒙审查规范

从 ArkTS／ArkUI 宿主核对变更后的 HAR 公开出口、状态归属及资源生命周期。

## 按变化读取

| 本次变化 | 本技能资料 |
|---|---|
| 方案前提、已确认的范围与取舍、职责及场景交接 | [设计依据](references/common/scope.md#11-设计依据与适用范围)、[职责](references/common/responsibilities.md)、[调用与组合](references/common/composition.md) |
| 状态、身份、异步收尾和资源 | [状态归属](references/common/state.md) |
| 公共输入输出、协议与业务结果 | [交接契约](references/common/contracts.md) |
| 测试证据、消费者与回归范围 | [测试责任](references/common/verification.md#72-测试责任)、[变更影响](references/common/verification.md#73-变更影响) |
| 新增或改变的失败路径 | [日志与故障诊断](references/common/verification.md#721-日志与故障诊断) |
| 原生工程、HAR 与公开入口 | [范围](references/harmony/scope.md)、[公开入口](references/harmony/files.md)；归属变化补[目录](references/harmony/directory.md) |
| 库状态、主题与布局 | [状态](references/harmony/state.md)、[UI](references/harmony/ui.md)，按实际变化选读 |
| 原生能力、协议与消费者 | [接入](references/harmony/integration.md)、[验证](references/harmony/testing.md) |

指出缺陷所在位置、触发条件、违反的契约及受影响的原生消费者。区分源码、实际 HAR、宿主和设备上能观测到的行为。
