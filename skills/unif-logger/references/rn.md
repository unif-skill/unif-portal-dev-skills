# RN 与 Web 日志

核对 package.json、exports 与实际安装版本，再按 docs 或对应的公开单页读取；website/docs 链接到同一文档来源：

| 任务 | 资料 |
|---|---|
| 安装、身份与应用生命周期 | [快速开始](https://unif-design.github.io/react-native-logger/md/quick-start.md) |
| 结构化记录、运行时、诊断与后端 | [根 API](https://unif-design.github.io/react-native-logger/md/api/root.md) |
| 原生／Web 文件适配、快照与交接 | [文件 API](https://unif-design.github.io/react-native-logger/md/api/files.md) |
| 字段、脱敏与 JSONL | [格式](https://unif-design.github.io/react-native-logger/md/FORMAT.md) |
| 故障定位与库内维护 | [排障](https://unif-design.github.io/react-native-logger/md/troubleshooting.md)、[开发](https://unif-design.github.io/react-native-logger/md/DEVELOPMENT.md) |

根入口与 `/files` 分开消费；原生 createLogFiles 接收 directoryName 和 createId，目录是应用私有日志子目录。Web 通过 browser 条件采用有界内存，不具备原生文件、快照和导出能力，不另造一个 Web 深层入口。

installLogging 选项只在首次安装生效。组件库和 SDK 日志接线共享宿主运行时；结构化 createLogger 与后端 Logger 的可变参数签名不同，不能互换。需要 defaultLogBackend 等接口时先查采用版本的根导出，不将 RN 新接口直接用于鸿蒙旧核心。

维护从 docs/DEVELOPMENT.md、src/index.ts、src/files 和真实宿主定位。涉及共享核心的变更先核对鸿蒙 logger-source.json，但不因同源而扩大单平台修改授权。

验证实际生产者→运行时→存储→导出消费者，覆盖匿名／登录、A→B→A、旧上下文、敏感字段、flush 失败、clear 后快照可读及交付后读取释放。Web 内存检查、原生 BlobUtil、打包消费与真实设备分开记录；不以日志函数被调用证明已落盘。
