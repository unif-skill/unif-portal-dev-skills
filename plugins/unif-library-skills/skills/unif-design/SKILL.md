---
name: unif-design
description: 在查询、接入、维护或排查 @unif/react-native-design 或 @unif/harmony-design 的基础组件、主题、字体、玻璃表面、UI 宿主及鸿蒙目标契约时使用。
metadata:
  package: "@unif/react-native-design"
  harmony_package: "@unif/harmony-design"
---

# Unif Design

原生鸿蒙的基础 UI、主题与展示宿主见[鸿蒙契约与实际库入口](references/harmony.md)。

## React Native

按锁定版本的包导出和公开类型核对下列资料。本地文档位于 `website/docs`，线上文档的构建版本见[官网索引](https://unif-design.github.io/react-native-design/llms.txt)。

| 任务 | 使用资料 |
|---|---|
| 安装、Provider 与宿主 | [getting-started](https://unif-design.github.io/react-native-design/md/getting-started.md) |
| 寻找已有组件与组合 | [components/overview](https://unif-design.github.io/react-native-design/md/components/overview.md) |
| 主题颜色与字体缩放 | [design/tokens/colors](https://unif-design.github.io/react-native-design/md/design/tokens/colors.md)、[design/tokens/typography](https://unif-design.github.io/react-native-design/md/design/tokens/typography.md) |
| 输入、图片和底部内容面板 | [components/input](https://unif-design.github.io/react-native-design/md/components/input.md)、[components/textarea](https://unif-design.github.io/react-native-design/md/components/textarea.md)、[components/image-preview](https://unif-design.github.io/react-native-design/md/components/image-preview.md)、[components/sheet](https://unif-design.github.io/react-native-design/md/components/sheet.md) |
| 确认、提示与玻璃表面 | [components/confirm](https://unif-design.github.io/react-native-design/md/components/confirm.md)、[components/toast](https://unif-design.github.io/react-native-design/md/components/toast.md)、[components/glass-layer](https://unif-design.github.io/react-native-design/md/components/glass-layer.md) |
| 测试接入与故障 | [testing](https://unif-design.github.io/react-native-design/md/testing.md)、[troubleshooting](https://unif-design.github.io/react-native-design/md/troubleshooting.md) |

## RN 使用边界

先查已有组件，再核对公开类型、示例和宿主。组件负责展示与必要 UI 状态，业务值、动作及主题／字体持久化归应用；应用字体系数在所属出口只处理一次。

颜色、间距和材质问题先检查所用主题、样式及组合；普通内部修改保留交互、可访问性及平台降级。涉及图标包时核对其采用版本的公开资料；已安装 unif-icons 时可按需使用。

源码维护与验证见[维护与组件验收](references/maintenance.md)。
