---
name: unif-icons
description: 选用已有图标、排查渲染和读屏问题，或维护共用的 SVG、命名和两端生成产物。对应 @unif/react-native-icons 和原生鸿蒙图标库 @unif/harmony-icons。
metadata:
  package: "@unif/react-native-icons"
  harmony_package: "@unif/harmony-icons"
---

# Unif Icons

## 在页面使用已有图标

先查消费者锁定的包版本，确认实际导出的图标名称与风格。装饰图标的可访问名称和焦点交给按钮等实际承载者。图标独立表达语义时，在图标上提供可访问名称。

| 平台 | 公开入口 | 尺寸、颜色 |
|---|---|---|
| RN | 包根或正式子路径中的命名组件。[RN 图标 API](https://unif-design.github.io/react-native-icons/md/api.md) | `size`、`color` |
| 原生鸿蒙 | 由 采用模块的 `oh-package.json5` 找到 HAR 导出的 `UnifIcon` 或命名组件。[鸿蒙公开入口与示例](references/harmony.md) | `iconSize`、`iconColor` |

颜色由页面提供。RN 宿主按版本配置 `react-native-svg`，普通消费无需运行生成器或引入 SVG transformer。[RN 版本与安装资料](https://unif-design.github.io/react-native-icons/llms.txt)

图标缺失或读屏重复时，先查实际导出的 Outlined／Filled 名称，再查调用处的颜色、尺寸和可访问属性。用对应平台的页面核对最终图形、颜色和读屏焦点。

## 新增图形或修改渲染

几何或命名变化从唯一 SVG 源和清单修改。运行现有生成器，检查授权范围内 RN、鸿蒙目标仓的实际产物、公开入口与示例。限定单端时，记录另一端受影响的产物。[贡献流程](https://unif-design.github.io/react-native-icons/md/contributing.md)

平台参数、渲染或无障碍行为有变化时，查各端手写组件，再用真实消费者核验行为。[同源生成与双端校验](references/workflows.md)
