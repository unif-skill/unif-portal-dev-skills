---
name: unif-umeng
description: 接入或维护友盟统计和渠道分享，定位隐私同意后的初始化、分享弹层与平台回调问题。RN 对应 @unif/react-native-umeng，原生鸿蒙覆盖 @unif/harmony-umeng 的目标契约与实际导出。
metadata:
  package: "@unif/react-native-umeng"
  harmony_package: "@unif/harmony-umeng"
---

# Unif Umeng

先从应用的隐私同意记录查起。取得真实同意后才调用 `initializeUmeng`，等待本地 SDK 初始化完成，再使用统计或分享。凭据留在宿主配置中，诊断和分享结果只保留必要字段。[隐私与初始化](https://unif-design.github.io/react-native-umeng/md/guides/privacy-pipl.md) · [统计](https://unif-design.github.io/react-native-umeng/md/guides/analytics.md)

查询接口时核对锁定版本的公开类型。RN 本地资料在 `website/docs`，官网索引标明构建版本。原生鸿蒙先看 HAR 实际入口，若入口为空，只能核对目标渠道及实现缺口。[RN 文档与版本索引](https://unif-design.github.io/react-native-umeng/llms.txt) · [鸿蒙公开入口与契约](references/harmony.md)

## 选择分享方式

| 场景 | 调用方式 |
|---|---|
| 渠道和内容都已确定 | 直接调用 `share`，由原调用接收结果。[分享接口](https://unif-design.github.io/react-native-umeng/md/api/share.md) |
| 内容已备好，让用户在 SDK 弹层选渠道 | 在展示窗口挂载 `useShareSheet` 返回的宿主，用同一实例的控制器打开。[弹层宿主](https://unif-design.github.io/react-native-umeng/md/api/platform-sharesheethost.md) |
| 在页面内先选渠道，再准备图片 | 用 `SharePanel`，要求 `@unif/react-native-umeng` 2.7.0 或更高版本。[2.7.0 页内渠道面板](https://github.com/unif-design/react-native-umeng/blob/v2.7.0/website/docs/api/platform-sharesheethost.md) |

在页内选渠道时，把 `getShareTargets()` 返回的渠道交给 `SharePanel`。收到 `onSelect` 后才由应用准备图片、上传并发起分享。

## 面板没有出现或收不到分享结果

面板不可见时先核对展示窗口、宿主与控制器的实例。面板关闭或渠道 App 被拉起后，继续查原分享调用的 `success`、`cancelled` 或 `failed`，在途冲突按 `busy` 等原因处理。

维护时从异常所属的初始化、分享或统计模块追到原生接线。在实际平台核对渠道回调，统计是否到达则查统计平台的接收情况。[维护与平台验证](references/workflows.md)
