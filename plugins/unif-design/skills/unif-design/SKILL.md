---
name: unif-design
description: 查找或维护 @unif/react-native-design 的基础组件、主题和弹层，排查字号、玻璃材质或宿主显示问题。原生鸿蒙对应 @unif/harmony-design 的公开导出与目标契约。
metadata:
  package: "@unif/react-native-design"
  harmony_package: "@unif/harmony-design"
---

# Unif Design

在 RN 页面找组件时，先查应用锁定版本的包导出和公开类型，按组件名称查看用法。本地文档在 `website/docs`，官网索引标明文档对应的版本。[组件目录](https://unif-design.github.io/react-native-design/md/components/overview.md) · [官网索引](https://unif-design.github.io/react-native-design/llms.txt)

原生鸿蒙从 HAR 清单的 `main` 查起。如果入口只有 `export {};`，只能说明目标组件的职责和实现缺口。有实际导出后，再核对其原生参数与消费者。[鸿蒙公开入口与目标契约](references/harmony.md)

## 在页面接入组件

先看页面已有的 Provider、弹窗宿主和组件。输入框把新值交还页面，确认框返回用户选择，后续业务动作由页面执行。主题和字体设置也由应用保存。需要图标时，从所用图标包的公开入口取对应版本的图标。[Provider 与宿主](https://unif-design.github.io/react-native-design/md/getting-started.md)

## 定位显示问题

| 现象 | 检查位置 |
|---|---|
| 应用字号放大了两次 | 从 Provider 的 `fontScale` 追到最终文字样式，确认应用字体系数只作用一次。[字体缩放](https://unif-design.github.io/react-native-design/md/design/tokens/typography.md) |
| 颜色、间距或玻璃效果异常 | 对照页面实际使用的主题、组件样式和平台降级效果。[玻璃表面](https://unif-design.github.io/react-native-design/md/components/glass-layer.md) |
| 确认框或提示没有出现 | 查发起调用的窗口以及该窗口能接收请求的 Confirm 或 Toast 宿主。[常见问题](https://unif-design.github.io/react-native-design/md/troubleshooting.md) |

修改库时，从出现问题的组件和实际使用它的页面入手。涉及共享主题或类型，再核对受影响组件。在消费者页面核对中文与系统大字号，分别观察文字、图标和控件尺寸，再检查触达区域、读屏和平台降级。[维护与组件验收](references/maintenance.md)
