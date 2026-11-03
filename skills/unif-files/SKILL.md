---
name: unif-files
description: 在查询、接入、维护或排查 @unif/react-native-files 的文件读写、复制、下载、目录清理、文件生命周期或本地 HTTP 资源访问时使用。不用于 Logger 专属日志文件管理。
metadata:
  package: "@unif/react-native-files"
---

# Unif Files

先核对实际包版本、锁文件、exports 和公开类型。[官网索引](https://unif-design.github.io/react-native-files/llms.txt) 只说明文档构建版本；版本不同则取得对应包或已核实修订的资料。所有消费从包公开入口进行。

## 按任务读取

本地资料位于 docs，website/docs 链接到同一来源；无库工作区时按任务读取下列单页。

| 任务 | 资料 |
|---|---|
| 原生依赖、补丁与本地网络策略 | [安装配置](https://unif-design.github.io/react-native-files/md/host-setup.md) |
| 文件读写、复制、删除与目录清理 | [文件操作](https://unif-design.github.io/react-native-files/md/api/file-operations.md) |
| 下载、进度、取消与失败文件 | [下载](https://unif-design.github.io/react-native-files/md/api/download.md) |
| 预览／上传持有与目录 URI | [生命周期](https://unif-design.github.io/react-native-files/md/api/lifetime.md) |
| WebView 等组件的本地 HTTP 资源 | [资源访问](https://unif-design.github.io/react-native-files/md/api/local-resources.md) |
| 结果类型与排障 | [类型](https://unif-design.github.io/react-native-files/md/api/types.md)、[常见问题](https://unif-design.github.io/react-native-files/md/troubleshooting.md) |

## 使用边界

复用实际文件操作和 createLocalFileLifetime，不在页面重复维护同一文件的持有状态。retain、retainRead 和 retire 分别表达持有、独占读取和待清理；取消或页面关闭不能证明原生读取已停止。清理时机依据实际使用者释放，异步删除结果由调用方处理。

复制／下载只清理本次拥有的失败产物，成功文件交给应用。目录清理使用功能专属目录，保留 partial 与 failed 结果，不清空应用根目录。下载结果、远端内容完整性和业务采用分别核实。

createLocalResourceAccess 由实际共享宿主持有。成功生成 URL 不证明文件存在或 WebView 已加载；所有消费者结束后再 close。目录边界检查不解析符号链接，不能作为不可信文件的安全隔离。

## 实施与验证

独立接入、源码维护与验证见[任务指引](references/workflows.md)。保留路径、所有权与原生终态保护；命令取当前 package.json/CI。类型与 Mock、修补 SDK、平台构建、设备文件／HTTP 行为分别报告，只查询接口不执行清理或安装。
