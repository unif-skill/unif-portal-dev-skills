---
name: unif-harmony-project
description: 在 Unif 原生鸿蒙应用或 @unif HAR 库中，需要组织 ArkTS 源码、对照 RN 公开接口，或核对宿主接线、资源交接和跨端验收时使用。仅从已有材料读出 SDK 版本、配置字段值或已发布 API 事实时不使用。
---

# Unif 原生鸿蒙工程

从宿主的依赖配置定位采用的原生模块、公开导出和实际导入它的 ArkUI 宿主。Portal 主应用和每个 HAR 分别以本工程采用的 RN 版本和 Git 修订为对照，原生实现使用 ArkTS、ArkUI 和本端 SDK。

## 核对 RN 行为和源码组织

1. 对照开发、重构或修正警告前，先查本工程采用记录，再读该修订的公开入口、实际调用链和契约。保持公开名称、参数与默认值、用户流程、状态变化、业务回执、失败、重试、取消和资源交接。测试预期从 RN 实际行为取得。资料缺失、RN 与契约冲突，或原生平台无法等价实现时，列出依据和影响，取得确认后再处理该差异。
2. 调整 ArkTS 文件时，按[ArkTS 文件与公共入口](references/harmony/files.md)和[工程目录](references/harmony/directory.md)查所属单元及已有文件。将模块级业务与协议常量归到所属功能的常量文件，将显式类型声明归到类型文件。共享纯工具放在现有工具单元，功能专用逻辑随所属功能维护。手写源码和入口使用 `.ets`，局部运行值、工具固定入口和生成文件按原职责维护。
3. 验收实际改动及消费者。对应同一输入核对两端的结果、时序和副作用，尤其是权限、错误、取消和重试。检查改动中是否出现 RN 没有的业务分支、兼容、公开项或默认行为，并逐文件确认常量、类型、工具和实现的归属。有差异时按第 1 步处理。

## 确认宿主实际能用什么

检查 HAR 的入口配置、入口文件的导出，以及宿主按包名导入的符号。空 HAR 可以验证打包流程。要确认某项能力可用，还需要包里的实现及调用该能力的宿主。

Icons、Design、Chat、Camera、HMS Scan、Umeng 的目标行为见所属库技能或[原生库规范](https://github.com/unif-design/unif-platform-architecture/tree/main/libraries)。Portal（原生鸿蒙）从 `ai-app-portal-harmony/entry/oh-package.json5` 定位采用的 HAR 包。同仓模块读 `packages/` 下的包清单和公开入口，注册表依赖核对锁定版本的 HAR。Logger 的文件能力从包的 `/Files` 入口取得。

## 沿页面生命周期检查资源

监听、Context 或回调属于启动它的宿主实例与登录周期。页面关闭再重开时，分别投递旧回调和当前回调，观察哪个实例被更新。处理借用图片等资源时，先查 SDK 何时真正结束读取，再确定调用方何时可以删除源文件。取消等待的回执按该 API 的约定解释。[状态与生命周期](references/harmony/state.md)

设备、HTTP／SSE 和 H5 调用还要查实际提供方、身份和业务回执。[原生接入](references/harmony/integration.md)说明交接责任。[原生 UI](references/harmony/ui.md)用于核对主题、字体、组件和玻璃效果在 ArkUI 宿主中的表现。

## 核实本次验收覆盖哪一层

按[鸿蒙验收对象](references/harmony/testing.md)记录 RN 行为基线、鸿蒙包版本、共同案例及本端验证。源码消费检查 Portal 构建与实际调用。按包分发还需用独立宿主检查 HAR 的导出、资源和依赖，发布后验证指定版本的安装。涉及身份和跨模块结果时，查 `$unif-platform-rules` 的 `references/architecture/state.md` 和 `references/architecture/contracts.md`。失败、降级和恢复的诊断责任见 `references/architecture/verification.md#721-日志与故障诊断`。

## 按任务选择工程方法

| 当前任务 | 方法入口 |
|---|---|
| 实施 ArkTS／ArkUI 改动 | `uni-code-change`；平台机制查 `uni-harmony-dev` |
| 定位宿主或 SDK 故障 | `uni-debugging` |
| 审查原生接线或配置差异 | `uni-code-review` |
| 设计生命周期、取消或回调交错用例 | `uni-test-design` |
| 选择 HAR、宿主或设备验收检查 | `uni-verify-change` |
| 维护 HAR 的工程、导出和产物 | `uni-harmony-library` |

已确定的跨仓契约变更使用 `unif-contract-change`。
