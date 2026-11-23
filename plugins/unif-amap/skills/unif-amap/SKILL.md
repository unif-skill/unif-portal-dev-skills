---
name: unif-amap
description: 接入 @unif/react-native-amap 的高德选点、定位或地点查询，排查 RN 宿主和高德应用唤起问题。其他地图库和原生鸿蒙地图接口另查对应库。
metadata:
  package: "@unif/react-native-amap"
---

# Unif AMap

先按应用锁文件和包根导出确认实际版本。本地资料在 `website/docs`，官网构建版本不同时，查对应修订的公开类型。[官网版本与操作索引](https://unif-design.github.io/react-native-amap/llms.txt)

## 接入地图或选点

从应用已有的权限、键盘、外部 URL 能力接入 `configureAmapHost`，取得真实隐私同意后才初始化高德。纯地图展示使用所用版本的底层地图组件。需要用户选点时，可直接渲染 `MapPicker`。函数式选点先挂载 `MapPickerHost`，再调用 `openMapPicker`。确认选择后，再由应用保存。[快速开始与宿主配置](https://unif-design.github.io/react-native-amap/md/quick-start.md)

## 取消选点后重开，出现了上次的地点

先查原调用的搜索或候选结果由谁采用。对照视野、查询中心、候选、待选和最终确认，区分程序移动视野与用户拖动。关闭或接替后，旧回调不能覆盖新选择。[事件与结果类型](https://unif-design.github.io/react-native-amap/md/api.md)

## 定位、地点查询和外部唤起

| 操作 | 可以从结果判断什么 |
|---|---|
| 持续定位 | `subscribed` 表示订阅已建立，位置要等本轮观测。旧句柄只能停止原观察。 |
| 地点查询 | 按传入的坐标系和参数发一次请求。定位、补查和翻页由调用方显式发起。 |
| 唤起高德 | 打开成功只表示系统已接收请求。异常时查系统能否处理该链接及实际打开结果。 |

维护控制器或原生调用时，先定位真实消费者，并核对宿主实际使用的 SDK 补丁。用取消重开和迟到回调验证选择归属，在实际设备检查键盘、手势、定位与地点查询。[原生宿主与补丁](https://unif-design.github.io/react-native-amap/md/native-host.md) · [维护与验证](references/workflows.md)
