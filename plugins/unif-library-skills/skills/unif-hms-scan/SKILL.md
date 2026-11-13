---
name: unif-hms-scan
description: 在查询、接入、维护或排查 @unif/react-native-hms-scan 或 @unif/harmony-hms-scan 的实时扫码、图片解码、权限、手电及鸿蒙目标契约时使用。
metadata:
  package: "@unif/react-native-hms-scan"
  harmony_package: "@unif/harmony-hms-scan"
---

# Unif HMS Scan

原生鸿蒙的相机权限与图片借用见[鸿蒙契约与实际库入口](references/harmony.md)。

## React Native

按锁定版本的包导出和公开类型核对下列资料。本地文档位于 `website/docs`，线上文档的构建版本见[官网索引](https://unif-design.github.io/react-native-hms-scan/llms.txt)。

| 任务 | 使用资料 |
|---|---|
| 安装与开始接入 | [getting-started/installation](https://unif-design.github.io/react-native-hms-scan/md/getting-started/installation.md)、[getting-started/quick-start](https://unif-design.github.io/react-native-hms-scan/md/getting-started/quick-start.md) |
| 现成扫码交互 | [guides/scanner](https://unif-design.github.io/react-native-hms-scan/md/guides/scanner.md)、[api/scanner](https://unif-design.github.io/react-native-hms-scan/md/api/scanner.md) |
| 自定义取景与事件 | [guides/headless](https://unif-design.github.io/react-native-hms-scan/md/guides/headless.md)、[api/hms-scan-view](https://unif-design.github.io/react-native-hms-scan/md/api/hms-scan-view.md) |
| 本地图片与借用生命周期 | [guides/decode-image](https://unif-design.github.io/react-native-hms-scan/md/guides/decode-image.md)、[api/functions](https://unif-design.github.io/react-native-hms-scan/md/api/functions.md) |
| 权限、手电和平台支持 | [guides/permissions](https://unif-design.github.io/react-native-hms-scan/md/guides/permissions.md)、[platform-differences](https://unif-design.github.io/react-native-hms-scan/md/platform-differences.md) |
| 结果、错误与验证 | [api/types](https://unif-design.github.io/react-native-hms-scan/md/api/types.md)、[testing](https://unif-design.github.io/react-native-hms-scan/md/testing.md)、[troubleshooting](https://unif-design.github.io/react-native-hms-scan/md/troubleshooting.md) |

## RN 使用边界

按任务选择 Scanner 的成品交互、HmsScanView 的自定义取景或 decodeImage 的图片识别。读取权限不应弹出授权；图片识别不需要相机权限，也不负责选图或下载。码值的商品、登录或客户含义由应用解释。

图片在识别结束前仍被借用，关闭页面不能提前删除；空结果、输入/桥接错误和 SDK 失败分别处理。手电请求与实际状态分开，平台支持范围、厂商静默失败和设备验证以对应版本资料为准。

源码维护与验证见[扫码接入与验证](references/workflows.md)。
