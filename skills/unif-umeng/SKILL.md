---
name: unif-umeng
description: 在查询、接入、维护或排查 @unif/react-native-umeng 或 @unif/harmony-umeng 的隐私同意后初始化、统计、分享、平台回调及鸿蒙目标契约时使用。
metadata:
  package: "@unif/react-native-umeng"
  harmony_package: "@unif/harmony-umeng"
---

# Unif Umeng

原生鸿蒙的初始化、渠道选择与分享回执见[鸿蒙契约与实际库入口](references/harmony.md)。

## React Native

按锁定版本的包导出和公开类型核对下列资料。本地文档位于 `website/docs`，线上文档的构建版本见[官网索引](https://unif-design.github.io/react-native-umeng/llms.txt)。

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

源码维护与验证见[分享接入与验证](references/workflows.md)。
