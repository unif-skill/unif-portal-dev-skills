# 原生鸿蒙日志

从实际 HAR 或库修订确认公开接口；版本读取 library/oh-package.json5，不能采用根目录 Node 工具包的版本。发布和 OHPM 审核状态另行核实；未取得可安装发布证据时，采用已验证 HAR 的 file 依赖，不假设中心仓已有包。

| 任务 | 所属仓库资料 |
|---|---|
| 接入、日志、身份与文件交接 | [library/README.md](https://github.com/unif-design/harmony-logger/blob/main/library/README.md) |
| HAR 根入口与文件入口 | [Index.ts](https://github.com/unif-design/harmony-logger/blob/main/library/Index.ts)、[Files.ts](https://github.com/unif-design/harmony-logger/blob/main/library/Files.ts)、[包清单](https://github.com/unif-design/harmony-logger/blob/main/library/oh-package.json5) |
| 日志格式 | [library/FORMAT.md](https://github.com/unif-design/harmony-logger/blob/main/library/FORMAT.md) |
| 核心采用与生成 | [logger-source.json](https://github.com/unif-design/harmony-logger/blob/main/logger-source.json)、[开发说明](https://github.com/unif-design/harmony-logger/blob/main/docs/DEVELOPMENT.md) |

以上链接用于定位；在本地按相同相对路径读取，涉及具体接口时使用采用修订而不是直接假设 main 兼容。

文件工厂从 `@unif/harmony-logger/Files` 导入，大小写有意义；它接收 context、directoryName 和 createId，使用 context.filesDir 下的私有目录。不能复制 RN `/files` 的导入与参数，也不引入 BlobUtil、RN、React 或 npm 运行时。文件 URI 保留鸿蒙系统生成的 authority，不自行改成 RN 路径形式。

共享核心按 logger-source.json 指定的 RN Git 修订生成；当前 RN main 和版本号不能代替采用记录。共同逻辑在所属来源修复，平台差异在 native 适配处理，不能手改 generated、Index.ts 或生成格式文档。更新采用修订属于源码维护，仅在本次授权覆盖时执行；纯 HAR 消费不运行生成器。

维护时按 docs/DEVELOPMENT.md 核对完整核心依赖、生成器、原生适配、来源清单与实际 example。使用现有 check:core、共享核心回归及 HAR 验包／独立消费入口；具体命令与 SDK 取当前工程，不要求消费者取得 RN 工作区。

验证真实生产者与文件消费者的身份切换、clear 后快照、交付后 dispose、读取完成释放和 SDK 写入／关闭失败。Node 替身、API 26 构建、独立 HAR 消费、设备运行与 OHPM 发布后安装分别记录，不能从其中一层推出其余通过。
