---
name: unif-harmony-project
description: 在 Unif 原生鸿蒙应用或 @unif HAR 库中，需要核对宿主接线、资源交接或跨端功能验收时使用。只查 SDK 版本或已发布 API 时查看相应资料。
---

# Unif 原生鸿蒙工程

从工程采用的原生修订，跟到 HAR 公开导出和实际导入它的 ArkUI 宿主。RN 与鸿蒙共同支持的功能要核对两端的业务语义，各端 API 和运行效果以对应原生工程为准。

## 确认宿主实际能用什么

检查 HAR 的入口配置、入口文件的导出，以及宿主按包名导入的符号。空 HAR 可以验证打包流程。要确认某项能力可用，还需要包里的实现及调用该能力的宿主。新建工程或移动文件时查看[实施范围](references/harmony/scope.md)、[工程目录](references/harmony/directory.md)和[公开入口](references/harmony/files.md)。

Icons、Design、Chat、Camera、HMS Scan、Umeng 的目标行为见所属库技能或[原生库规范](https://github.com/unif-design/unif-platform-architecture/tree/main/libraries)。Logger 采用哪个共享核心，要核对本库 `logger-source.json` 所锁定的 RN 修订，以及生成后的 HAR 是否导出所需的 `Files` 等能力。[Logger 原生公开接口](https://github.com/unif-design/harmony-logger/blob/main/library/README.md)

## 沿页面生命周期检查资源

监听、Context 或回调属于启动它的宿主实例与登录周期。页面关闭再重开时，分别投递旧回调和当前回调，观察哪个实例被更新。处理借用图片等资源时，先查 SDK 何时真正结束读取，再确定调用方何时可以删除源文件。取消等待的回执按该 API 的约定解释。[状态与生命周期](references/harmony/state.md)

设备、HTTP／SSE 和 H5 调用还要查实际提供方、身份和业务回执。[原生接入](references/harmony/integration.md)说明交接责任。[原生 UI](references/harmony/ui.md)用于核对主题、字体、组件和玻璃效果在 ArkUI 宿主中的表现。

## 核实本次验收覆盖哪一层

按[鸿蒙验收对象](references/harmony/testing.md)分别记录共享逻辑用例、ArkTS 编译、HAR 导入、真实宿主、设备操作和业务回执的结果。涉及身份和跨模块结果时，查 `$unif-platform-rules` 的 `references/architecture/state.md` 和 `references/architecture/contracts.md`。失败、降级和恢复的诊断责任见 `references/architecture/verification.md#721-日志与故障诊断`。

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
