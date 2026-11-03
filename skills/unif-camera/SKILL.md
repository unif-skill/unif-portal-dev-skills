---
name: unif-camera
description: 在查询、接入、维护或排查 @unif/react-native-camera 或 @unif/harmony-camera 的拍照、录像、水印、宿主、媒体交接及原生目标契约时使用。
metadata:
  package: "@unif/react-native-camera"
  harmony_package: "@unif/harmony-camera"
---

# Unif Camera

先确定 RN 或原生鸿蒙，再核对采用版本、公开入口与实际实现。目标契约、空 HAR、已实现 API 和已发布产物分别判断；不把 RN 接口改包名当作鸿蒙用法。

## 按平台读取

| 目标 | 入口 |
|---|---|
| React Native | 下方 RN 资料与当前包公开类型 |
| 原生鸿蒙 | [鸿蒙接入与契约](references/harmony.md)；先核对实际库，再按任务读取目标规范 |

独立消费只需本技能完整目录及对应库资料，不要求安装另一平台或其他技能。技能资料本身不授权恢复暂停的产品开发。

## RN 资料

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-camera/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

本地源码的使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读当前任务相关单页，全文是确需全局资料时的选项。

| 任务 | 使用资料 |
|---|---|
| 依赖与原生安装 | [getting-started/installation](https://unif-design.github.io/react-native-camera/md/getting-started/installation.md) |
| 开始拍摄与宿主 | [getting-started/quick-start](https://unif-design.github.io/react-native-camera/md/getting-started/quick-start.md)、[api/use-camera](https://unif-design.github.io/react-native-camera/md/api/use-camera.md) |
| 调用、替换、取消与媒体归属 | [getting-started/concepts](https://unif-design.github.io/react-native-camera/md/getting-started/concepts.md)、[api/camera-api](https://unif-design.github.io/react-native-camera/md/api/camera-api.md)、[api/types](https://unif-design.github.io/react-native-camera/md/api/types.md) |
| 照片、录像与水印 | [guides/taking-photos](https://unif-design.github.io/react-native-camera/md/guides/taking-photos.md)、[guides/recording-video](https://unif-design.github.io/react-native-camera/md/guides/recording-video.md)、[guides/watermark](https://unif-design.github.io/react-native-camera/md/guides/watermark.md) |
| 迁移与排障 | [migration](https://unif-design.github.io/react-native-camera/md/migration.md)、[troubleshooting](https://unif-design.github.io/react-native-camera/md/troubleshooting.md) |
| Mock 与平台验证 | [testing](https://unif-design.github.io/react-native-camera/md/testing.md) |

## RN 使用边界

拍照、取景、预览和选择优先使用库已有交互。先核对 useCamera、返回的 holder 与 open 的当前公开类型；输入配置和结果采用归调用方。success 表示用户选用了媒体，文件仍是临时文件，保存与上传另行完成。

库只收回本轮拥有且尚未交付的文件；成功交付后由消费者维护文件生命周期。取消、替换调用和宿主卸载需要分别核对，旧调用不能污染新调用。局部拍照或处理失败保留已有媒体，不以失败原图替代合格产物。

## RN 实施与验证

本技能可单独使用，完整操作和维护依据见[任务指引](references/workflows.md)。应用消费采用公开接口和已有能力；源码维护从库内 docs/DEVELOPMENT.md 取得工程指定的规范。工程已配置共用阶段技能时按需使用，无需为本技能另行安装。复用同一任务已取得的有效依据。

验证实际输入、事件、结果与消费者，保留本库取消、错误和资源保护；检查命令从当前 package.json/CI 取得。只查询接口或版本时回答已核实事实，不自动修改代码、安装依赖或执行发布。
