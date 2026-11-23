---
name: unif-files
description: 管理 @unif/react-native-files 的文件读写、复制、下载与目录清理，排查预览和上传共用文件或 WebView 本地 HTTP 访问问题。Logger 的私有日志文件和诊断快照归日志库。
metadata:
  package: "@unif/react-native-files"
---

# Unif Files

从锁定版本的包根确认所需操作。文件读写、复制、下载和目录清理各有自己的结果类型。本地资料在 `docs`，官网索引标明文档对应的版本。[文件操作与版本索引](https://unif-design.github.io/react-native-files/llms.txt)

## 预览和上传还在用同一文件

先找文件创建者、实际读者和最终清理者，用同一个 `createLocalFileLifetime` 管理这份文件。

- **预览**用 `retain` 登记持有，在预览实际结束读取后归还。
- **需要独占读取的上传**用 `retainRead` 登记，等上传方确认原生已结束读取再归还。页面退出和取消上传都可能早于读取结束。

调用 `retire` 只标记文件待清理。包括预览和上传在内的所有持有者都归还后才触发清理，异步删除结果由调用方处理。排查提前删除时，逐一核对这两个读取者的释放时刻。[文件生命周期](https://unif-design.github.io/react-native-files/md/api/lifetime.md)

## WebView 地址生成了，页面仍加载失败

检查共享宿主持有的 `createLocalResourceAccess`、指定根目录和文件是否存在可读，再检查服务是否工作及 WebView 的实际加载结果。`getUrl` 成功只交付地址。全部消费者结束后才 `close`。路径边界检查不解析符号链接，宿主负责隔离不可信文件。[本地资源访问](https://unif-design.github.io/react-native-files/md/api/local-resources.md)

## 下载、清理与维护

复制或下载失败只清理本次拥有的产物。下载成功表示响应内容已保存，远端内容完整性另行核对，成功文件交给调用方。清目录仅针对功能专属目录，保留 `partial`、`failed` 和失败项。[下载与取消](https://unif-design.github.io/react-native-files/md/api/download.md) · [清理结果](https://unif-design.github.io/react-native-files/md/api/file-operations.md)

维护时从异常的文件操作或本地服务追到所属平台实现，核对宿主实际使用的依赖和补丁。验证取消后的文件归属、多读者释放、端口关闭及受影响的实际消费者。[维护与验证](references/workflows.md)
