---
name: unif-camera
description: 接入拍照、录像与水印，排查相机宿主和临时媒体交接。覆盖 @unif/react-native-camera 的公开用法与库内维护，也可核对原生鸿蒙 @unif/harmony-camera 的拍摄契约与实现状态。
metadata:
  package: "@unif/react-native-camera"
  harmony_package: "@unif/harmony-camera"
---

# Unif Camera

RN 先按应用锁定的包版本查拍照、录像和水印配置。本地文档在 `website/docs`，官网索引标明构建版本。原生鸿蒙先查 HAR 实际导出，遇到空入口时说明目标能力及实现缺口。[RN 配置与版本索引](https://unif-design.github.io/react-native-camera/llms.txt) · [鸿蒙库入口与媒体契约](references/harmony.md)

## 从打开相机到交付文件

1. 找到应用已有拍摄入口，复用库提供的取景、预览和选用界面。在稳定的组件树挂载 `useCamera` 返回的 `holder`，由同一实例的 `open` 开始本轮拍摄。[调用与宿主](https://unif-design.github.io/react-native-camera/md/api/use-camera.md)
2. 按原调用返回的 `success`、`cancelled` 或 `failed` 处理。只有用户选用媒体后，消费者才接手返回的临时文件。随后由应用调用已有保存或上传能力并检查其回执。[结果类型](https://unif-design.github.io/react-native-camera/md/api/types.md)

## 宿主退出、调用被替换或媒体丢失

打不开相机时，先查原调用的错误和实际挂载的宿主。媒体丢失时，查文件在哪一轮产生、用户是否已选用，以及谁还在读取。取消、调用接替和宿主卸载都只处理本轮资源。库回收自己尚未交付的文件，已交付文件等实际消费者读完再清理。[取消与替换](https://unif-design.github.io/react-native-camera/md/api/camera-api.md)

维护时从出错的会话或原生文件处理入手。局部拍照或处理失败要保留已有媒体，只交付满足要求的产物。改变裁切、方向、水印或录像收尾时，检查设备产生的实际文件及消费者能否读取。[维护与媒体验收](references/workflows.md)
