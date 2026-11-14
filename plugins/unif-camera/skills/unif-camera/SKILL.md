---
name: unif-camera
description: 在查询、接入、维护或排查 @unif/react-native-camera 或 @unif/harmony-camera 的拍照、录像、水印、宿主、媒体交接及鸿蒙目标契约时使用。
metadata:
  package: "@unif/react-native-camera"
  harmony_package: "@unif/harmony-camera"
---

# Unif Camera

原生鸿蒙拍摄的设备权限、媒体验收与文件归属见[鸿蒙契约与实际库入口](references/harmony.md)。

## React Native

按锁定版本的包导出和公开类型核对下列资料。本地文档位于 `website/docs`，线上文档的构建版本见[官网索引](https://unif-design.github.io/react-native-camera/llms.txt)。

| 任务 | 使用资料 |
|---|---|
| 依赖与原生安装 | [getting-started/installation](https://unif-design.github.io/react-native-camera/md/getting-started/installation.md) |
| 开始拍摄与宿主 | [getting-started/quick-start](https://unif-design.github.io/react-native-camera/md/getting-started/quick-start.md)、[api/use-camera](https://unif-design.github.io/react-native-camera/md/api/use-camera.md) |
| 调用、替换、取消与媒体归属 | [getting-started/concepts](https://unif-design.github.io/react-native-camera/md/getting-started/concepts.md)、[api/camera-api](https://unif-design.github.io/react-native-camera/md/api/camera-api.md)、[api/types](https://unif-design.github.io/react-native-camera/md/api/types.md) |
| 照片、录像与水印 | [guides/taking-photos](https://unif-design.github.io/react-native-camera/md/guides/taking-photos.md)、[guides/recording-video](https://unif-design.github.io/react-native-camera/md/guides/recording-video.md)、[guides/watermark](https://unif-design.github.io/react-native-camera/md/guides/watermark.md) |
| 排障 | [troubleshooting](https://unif-design.github.io/react-native-camera/md/troubleshooting.md) |
| Mock 与平台验证 | [testing](https://unif-design.github.io/react-native-camera/md/testing.md) |

## RN 使用边界

拍照、取景、预览和选择优先使用库已有交互。先核对 useCamera、返回的 holder 与 open 的当前公开类型；输入配置和结果采用归调用方。success 表示用户选用了媒体，文件仍是临时文件，保存与上传另行完成。

库只收回本轮拥有且尚未交付的文件；成功交付后由消费者维护文件生命周期。取消、替换调用和宿主卸载需要分别核对，旧调用不能污染新调用。局部拍照或处理失败保留已有媒体，不以失败原图替代合格产物。

源码维护与验证见[任务指引](references/workflows.md)。
