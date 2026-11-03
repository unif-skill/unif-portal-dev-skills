---
name: unif-design
description: 在查询、接入、维护或排查 @unif/react-native-design 或 @unif/harmony-design 的基础组件、主题、字体、玻璃表面、UI 宿主及鸿蒙目标契约时使用。
metadata:
  package: "@unif/react-native-design"
  harmony_package: "@unif/harmony-design"
---

# Unif Design

按下方入口选择 RN 或原生鸿蒙资料。目标契约不代表当前包已实现或发布；不把 RN 接口改包名当作鸿蒙用法。

## 按平台读取

| 目标 | 入口 |
|---|---|
| React Native | 下方 RN 资料与当前包公开类型 |
| 原生鸿蒙 | [鸿蒙接入与契约](references/harmony.md)；先核对实际库，再按任务读取目标规范 |

独立消费只需本技能完整目录及对应库资料，不要求安装另一平台或其他技能。

## RN 资料

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-design/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

本地使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读所需组件和组合单页，完整 API 从采用版本的公开类型取得。

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

## RN 维护与验证

源码维护或核对目标职责时读取[维护与契约](references/maintenance.md)及库内 docs/DEVELOPMENT.md。应用只消费组件时使用当前公开资料，无需架构仓或其他技能。

验证真实组件、事件、受控数据及本次消费者。布局与交互变化在可比条件下检查主题、大字号、键盘、触达与可访问性；类型、Mock、Web、原生和设备证据分别报告。检查命令从当前 package.json/CI 取得，只查询接口或版本时不启动开发和发布。
