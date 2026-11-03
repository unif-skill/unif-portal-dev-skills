---
name: unif-amap
description: 在查询、接入、维护或排查 @unif/react-native-amap 的地图选点、定位、地点查询、高德应用唤起及宿主接入时使用。不用于其他地图库或原生鸿蒙地图接口。
metadata:
  package: "@unif/react-native-amap"
---

# Unif AMap

先核对实际依赖、锁文件、package.json 的公开入口与类型。[官网索引](https://unif-design.github.io/react-native-amap/llms.txt) 标明文档构建版本；与采用版本不同时，使用对应包或已核实修订的资料。目标设计不证明当前包已有能力。

## 按任务读取

有库工作区时从 website/docs 读取对应页；没有时使用下列资料，不预读整站。

| 任务 | 资料 |
|---|---|
| 安装、隐私初始化与权限／键盘宿主 | [快速开始](https://unif-design.github.io/react-native-amap/md/quick-start.md) |
| 选点组件、函数式调用与控制器 | [API](https://unif-design.github.io/react-native-amap/md/api.md) 的 MapPicker 部分 |
| 单次／持续定位、地点查询、外部高德 | [API](https://unif-design.github.io/react-native-amap/md/api.md) 对应部分 |
| SDK 补丁、原生配置与验证 | [原生宿主](https://unif-design.github.io/react-native-amap/md/native-host.md) |
| 源码维护与真实消费者 | [任务指引](references/workflows.md) |

## 使用边界

复用应用已有权限、键盘和外部 URL 能力，通过 configureAmapHost 接线；隐私同意由应用持有，取得真实同意后才初始化高德。选点使用 MapPicker 或 MapPickerHost/openMapPicker；纯地图展示按库文档使用底层地图组件，不额外引入选点流程。

视野、查询中心、候选、待选和最终确认分别按公开契约交接。移动相机不等于用户拖图；success 只表示确认选择，业务保存属于应用。取消、替换和关闭后的迟到结果不能污染新调用。

定位、查询和外部应用唤起是不同操作。查询不隐式定位、补查或自动翻页；采用真实坐标系与返回字段。持续定位的 subscribed 不证明已经取得位置，旧句柄不能停止新观察。外部应用打开成功只表示系统接收交接。

## 实施与验证

本技能可独立使用；命令、peer 和原生前置从采用版本取得。应用消费已有公开能力，维护库时再读取 docs/DEVELOPMENT.md 与实际实现。只查询接口不自动安装、修改或发布。

核对实际消费者的确认、取消、权限、结果采用和释放。Web 不支持结果、Mock、库 CI、已修补 SDK、原生构建与设备高德服务结果分别报告。
