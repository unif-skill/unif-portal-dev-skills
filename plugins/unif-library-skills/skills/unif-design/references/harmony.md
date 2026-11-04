# 原生鸿蒙 Design

先读 [harmony-design README](https://github.com/unif-design/harmony-design/blob/main/README.md)、[包清单](https://github.com/unif-design/harmony-design/blob/main/library/oh-package.json5)及其 main 指向的入口；[目标契约](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-design.md)说明职责与验收，不证明组件已经导出。本地按相同路径读取，并采用工程指定的有效规范修订。

若工程仍为空 HAR、入口只有 `export {};`，只能核对目标与缺口，不能给出可运行的组件导入、OHPM 安装或接入完成结论。功能实现按当前任务授权开展；仅查询或补技能不启动实现。已有实现时，再按真实公开类型与消费者继续，不把技能中的规划判断固定成永久状态。

## 按目标核对

- 主题、基础数据、字体和原生样式按各自来源核对；应用字号在所属出口处理一次。RN tokens、Provider、Hook 和样式对象不直接成为 ArkUI 接口。
- 基础控件、输入、确认、Toast 与玻璃表面逐项对照实际原生出口及场景；一组按钮完成不能代表整个 Design 可消费。
- 业务值、持久化、确认后动作和最终业务结果仍归应用。UIContext、弹窗资源与呈现归实际宿主；旧回调不能处理新请求。

真实参数、系统材质能力与支持范围从采用库和 SDK 取得，不把目标文档里的示例或 RN API 当作已存在的鸿蒙签名。按工程已采用规范核对 ArkUI 与 SDK 用法。

## 实施与验收入口

有开发授权时，从所属仓库 AGENTS.md、README 与目标契约追踪真实组件、资源、依赖和消费者，优先复用已实现的原生能力。共享数据与各平台适配保持同源和真实差异。

源码／自动化、独立 HAR 与 ArkUI 宿主、设备主题／大字号／键盘／读屏／玻璃效果、业务消费者分别验收。空 HAR 构建仅证明工程配置，不能替代组件、交互或发布证据。
