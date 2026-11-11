---
name: unif-umeng
description: 在查询、接入、维护或排查 @unif/react-native-umeng 或 @unif/harmony-umeng 的隐私同意后初始化、统计、分享、平台回调及鸿蒙目标契约时使用。
metadata:
  package: "@unif/react-native-umeng"
  harmony_package: "@unif/harmony-umeng"
---

# Unif Umeng

按下方入口选择 RN 或原生鸿蒙资料。目标契约不代表当前包已实现或发布；不把 RN 接口改包名当作鸿蒙用法。

## 按平台读取

| 目标 | 入口 |
|---|---|
| React Native | 下方 RN 资料与当前包公开类型 |
| 原生鸿蒙 | [鸿蒙接入与契约](references/harmony.md)；先核对实际库，再按任务读取目标规范 |

独立消费只需本技能完整目录及对应库资料，不要求安装另一平台或其他技能。

## RN 资料

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-umeng/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

本地源码的使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读当前任务相关单页，全文是确需全局资料时的选项。

| 任务 | 使用资料 |
|---|---|
| 安装与快速接入 | [getting-started/installation](https://unif-design.github.io/react-native-umeng/md/getting-started/installation.md)、[getting-started/quick-start](https://unif-design.github.io/react-native-umeng/md/getting-started/quick-start.md) |
| 隐私同意与初始化 | [guides/privacy-pipl](https://unif-design.github.io/react-native-umeng/md/guides/privacy-pipl.md)、[api/common](https://unif-design.github.io/react-native-umeng/md/api/common.md) |
| 直接分享与结果 | [guides/sharing](https://unif-design.github.io/react-native-umeng/md/guides/sharing.md)、[api/share](https://unif-design.github.io/react-native-umeng/md/api/share.md) |
| SDK 分享弹层与页内渠道列表 | [实例宿主](https://unif-design.github.io/react-native-umeng/md/api/platform-sharesheethost.md)、[SharePanel](https://unif-design.github.io/react-native-umeng/docs/api/platform-sharesheethost#share-panel) |
| 统计与原生回调 | [guides/analytics](https://unif-design.github.io/react-native-umeng/md/guides/analytics.md)、[api/analytics](https://unif-design.github.io/react-native-umeng/md/api/analytics.md)、[native-setup/ios](https://unif-design.github.io/react-native-umeng/md/native-setup/ios.md)、[native-setup/android](https://unif-design.github.io/react-native-umeng/md/native-setup/android.md) |
| 测试与排障 | [testing](https://unif-design.github.io/react-native-umeng/md/testing.md)、[troubleshooting](https://unif-design.github.io/react-native-umeng/md/troubleshooting.md) |

## RN 使用边界

应用取得真实隐私同意后再调用 initializeUmeng；库不拥有用户同意记录。导入包、显示面板和接收系统回调不等于完成初始化。配置与凭据不写入模型输入、日志或分享结果。

目标和内容已确定时调用 `share`。内容已备好、需要 SDK 弹层选渠道时使用 `useShareSheet`，在实际展示窗口挂载同一实例的宿主。`@unif/react-native-umeng` 2.7.0 起，页面内先选渠道再准备内容时使用 `SharePanel`，图片准备和上传由应用负责。

按分享结果处理 `success`、`cancelled` 和 `failed`，失败时区分 `busy` 等原因。面板关闭或第三方应用被拉起后，仍以原分享调用的结果为准。

## RN 实施与验证

应用消费采用当前公开接口；源码维护与定向验证见[任务指引](references/workflows.md)，工程规则从库内 docs/DEVELOPMENT.md 取得。复用同一任务已有且仍适用的依据。

检查命令取当前 package.json/CI；验证本次消费者及受影响的取消、错误和资源交接。仅查询接口或版本时不自动修改、安装或发布。
