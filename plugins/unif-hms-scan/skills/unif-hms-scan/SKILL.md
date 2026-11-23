---
name: unif-hms-scan
description: 选择实时扫码或图片解码，定位相机权限、手电状态和图片占用问题。涉及 @unif/react-native-hms-scan 的调用与维护，以及原生鸿蒙 @unif/harmony-hms-scan 的目标契约与实际导出。
metadata:
  package: "@unif/react-native-hms-scan"
  harmony_package: "@unif/harmony-hms-scan"
---

# Unif HMS Scan

先确认采用的包和版本。RN 的本地文档在 `website/docs`。原生鸿蒙查实际 HAR 入口，入口仅有 `export {};` 时按目标契约说明缺少的能力。[RN 文档与版本索引](https://unif-design.github.io/react-native-hms-scan/llms.txt) · [鸿蒙扫码契约与实际入口](references/harmony.md)

## 选择识别方式

| 场景 | RN 入口 | 前置条件 |
|---|---|---|
| 完整扫码界面 | [Scanner](https://unif-design.github.io/react-native-hms-scan/md/guides/scanner.md) | 需要从相册扫码时，由应用提供选图入口。 |
| 自定义实时取景 | [HmsScanView](https://unif-design.github.io/react-native-hms-scan/md/guides/headless.md) | 读取相机权限，按需申请，取得授权后挂载。 |
| 识别已有图片 | [decodeImage](https://unif-design.github.io/react-native-hms-scan/md/guides/decode-image.md) | 应用提供可读的本地文件，无需相机权限。 |

图片由应用下载或选取。归还临时图片的时机取决于实际读取者。

- 图片交给 `Scanner` 时，等 `ScannerImage.onSourceReleased` 通知。
- 直接调用 `decodeImage` 时，等本次 Promise 结算，即使页面已关闭也要保留文件到读取结束。

识别成功后把码值、码制交给应用，由应用解释商品、登录或客户含义。

## 核对识别结果和设备状态

空数组表示本次 SDK 未交付码。出现输入、桥接或 SDK 错误时，保留实际来源及原因。手电无响应时，核对 `onTorchState` 实际反馈、当前设备支持及厂商静默失败的情形。[平台差异](https://unif-design.github.io/react-native-hms-scan/md/platform-differences.md)

维护时从出问题的权限、解码或视图事件追到原生实现和实际消费者。分别验证无结果、多结果、错误、取消和重新挂载。手电、系统权限及图片方向在相应设备上核验。[维护与设备验证](references/workflows.md)
