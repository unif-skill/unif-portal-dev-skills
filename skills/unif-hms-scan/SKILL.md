---
name: unif-hms-scan
description: 在查询、接入、维护或排查 @unif/react-native-hms-scan 或 @unif/harmony-hms-scan 的实时扫码、图片解码、权限、手电及原生目标契约时使用。
metadata:
  package: "@unif/react-native-hms-scan"
  harmony_package: "@unif/harmony-hms-scan"
---

# Unif HMS Scan

先确定 RN 或原生鸿蒙，再核对采用版本、公开入口与实际实现。目标契约、空 HAR、已实现 API 和已发布产物分别判断；不把 RN 接口改包名当作鸿蒙用法。

## 按平台读取

| 目标 | 入口 |
|---|---|
| React Native | 下方 RN 资料与当前包公开类型 |
| 原生鸿蒙 | [鸿蒙接入与契约](references/harmony.md)；先核对实际库，再按任务读取目标规范 |

独立消费只需本技能完整目录及对应库资料，不要求安装另一平台或其他技能。技能资料本身不授权恢复暂停的产品开发。

## RN 资料

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-hms-scan/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

本地源码的使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读当前任务相关单页，全文是确需全局资料时的选项。

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

## RN 实施与验证

本技能可单独使用，完整操作和维护依据见[任务指引](references/workflows.md)。应用消费采用公开接口和已有能力；源码维护从库内 docs/DEVELOPMENT.md 取得工程指定的规范。工程已配置共用阶段技能时按需使用，无需为本技能另行安装。复用同一任务已取得的有效依据。

验证实际输入、事件、结果与消费者，保留本库取消、错误和资源保护；检查命令从当前 package.json/CI 取得。只查询接口或版本时回答已核实事实，不自动修改代码、安装依赖或执行发布。
