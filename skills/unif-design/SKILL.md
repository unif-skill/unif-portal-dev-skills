---
name: unif-design
description: 在使用、维护或排查 @unif/react-native-design 的基础组件、主题、字体、玻璃表面或 UI 宿主时使用。
metadata:
  package: "@unif/react-native-design"
---

# Unif Design

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-design/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

## 按任务读取

本地使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读所需组件和组合单页，完整 API 从采用版本的公开类型取得。

| 任务 | 使用资料 |
|---|---|
| 安装、Provider 与宿主 | [getting-started](https://unif-design.github.io/react-native-design/md/getting-started.md) |
| 寻找已有组件与组合 | [components/overview](https://unif-design.github.io/react-native-design/md/components/overview.md) |
| 主题颜色与字体缩放 | [design/tokens/colors](https://unif-design.github.io/react-native-design/md/design/tokens/colors.md)、[design/tokens/typography](https://unif-design.github.io/react-native-design/md/design/tokens/typography.md) |
| 输入、图片和底部内容面板 | [components/input](https://unif-design.github.io/react-native-design/md/components/input.md)、[components/textarea](https://unif-design.github.io/react-native-design/md/components/textarea.md)、[components/image-preview](https://unif-design.github.io/react-native-design/md/components/image-preview.md)、[components/sheet](https://unif-design.github.io/react-native-design/md/components/sheet.md) |
| 确认、提示与玻璃表面 | [components/confirm](https://unif-design.github.io/react-native-design/md/components/confirm.md)、[components/toast](https://unif-design.github.io/react-native-design/md/components/toast.md)、[components/glass-layer](https://unif-design.github.io/react-native-design/md/components/glass-layer.md) |
| 测试接入与故障 | [testing](https://unif-design.github.io/react-native-design/md/testing.md)、[troubleshooting](https://unif-design.github.io/react-native-design/md/troubleshooting.md) |

## 使用边界

先按组件概览查已有能力，再核对所用组件的类型、示例和宿主。应用提供业务值与动作，组件负责展示和明确的 UI 状态；主题与字体设置的持久化归应用。应用字体系数在所属出口处理一次，系统文字缩放、文字 metric 与布局尺寸保持各自语义。

颜色、间距和材质问题先检查所用主题、样式及组合；普通内部修改保留交互、可访问性及平台降级。涉及图标包时核对其采用版本的公开资料；已安装 unif-icons 时可按需使用。

## 维护与验证

本技能可单独使用。需要源码维护或核对目标职责时读取[维护与契约](references/maintenance.md)，从库内 docs/DEVELOPMENT.md 取得工程指定的规范；工程已配置 code-development、code-testing、code-review 或 code-delivery 时按实际阶段使用。应用只消费组件时采用公开资料，无需架构仓或其他技能。

验证真实组件、事件、受控数据及本次消费者。布局与交互变化在可比条件下检查主题、大字号、键盘、触达与可访问性；类型、Mock、Web、原生和设备证据分别报告。检查命令从当前 package.json/CI 取得，只查询接口或版本时不启动开发和发布。
