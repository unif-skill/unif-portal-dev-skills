# 原生鸿蒙日志

Portal（原生鸿蒙）在 `ai-app-portal-harmony` 开发。读 `entry/oh-package.json5` 及锁文件，确认 `@unif/harmony-logger` 的依赖来源。同仓源码位于 `packages/logger`，其他应用采用 OHPM 版本时检查所装 HAR 的公开声明。

| 要核对什么 | Portal 工程位置 |
|---|---|
| 版本、包身份和导出配置 | `packages/logger/oh-package.json5` |
| 根入口和文件入口 | `packages/logger/Index.ets`、`packages/logger/Files.ets` |
| 使用方法与验收入口 | `packages/logger/README.md` |
| 日志格式与 RN 行为对照 | `packages/logger/FORMAT.md`、`docs/acceptance/rn-harmony-parity.md` |

文件工厂从 `@unif/harmony-logger/Files` 导入，大小写有意义。工厂接收 `context`、`directoryName` 和 `createId`，使用 `context.filesDir` 下的私有目录。保留系统文件 URI 的 authority，参数以鸿蒙公开入口为准。

维护鸿蒙实现时读取本端包版本和公开类型。按 RN 包版本和 Git 修订选择共同案例，在功能对照表记录对齐目标与本端结果。0.3.0 的 `captureError` 通过 Promise 返回诊断文本或 `null`。

用真实日志生产者和文件接收方核对身份切换、clear 后快照、交付后 dispose、读取完成释放及 SDK 写入或关闭失败。按实际交付分别记录 Node 回归、Portal 原生编译、设备文件行为。独立发包时用实际产出的 HAR 验证公开入口、资源和依赖。使用方采用 OHPM 版本时，从目标仓安装指定版本，核对锁文件并编译实际导入。
