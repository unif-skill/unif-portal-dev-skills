---
name: unif-icons
description: 在查询、使用、维护或排查 @unif/react-native-icons、@unif/harmony-icons 的图标，或调整唯一 SVG／命名源及两端生成产物时使用。
metadata:
  package: "@unif/react-native-icons"
  harmony_package: "@unif/harmony-icons"
---

# Unif Icons

按下方入口选择 RN 或原生鸿蒙资料。目标契约不代表当前包已实现或发布；不把 RN 接口改包名当作鸿蒙用法。

## 按平台读取

| 目标 | 入口 |
|---|---|
| React Native | 下方 RN 资料与当前包公开类型 |
| 原生鸿蒙 | [鸿蒙接入与契约](references/harmony.md)；先核对实际库，再按任务读取目标规范 |

独立消费只需本技能完整目录及对应库资料，不要求安装另一平台或其他技能。

## RN 资料

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-icons/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

本地源码的使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读当前任务相关单页，全文是确需全局资料时的选项。

| 任务 | 使用资料 |
|---|---|
| 安装、导入与宿主依赖 | [getting-started](https://unif-design.github.io/react-native-icons/md/getting-started.md) |
| 图标 props 与可访问性 | [api](https://unif-design.github.io/react-native-icons/md/api.md) |
| 新增图形源与生成流程 | [contributing](https://unif-design.github.io/react-native-icons/md/contributing.md) |

## RN 使用边界

应用消费已有图标时从实际版本的公开出口选择名称与风格，使用 size、color 等公开属性；颜色由消费者提供，图标不隐式读取 Design 主题。操作按钮的可访问名称由实际承载者提供，独立表达语义的图标按 API 设置。

图形或命名变化从唯一 SVG 源和清单修改，生成与校验流程见[任务指引](references/workflows.md)。平台参数、渲染及可访问性分别核验，资源生成不能替代行为迁移；普通消费无需运行生成器或引入 SVG transformer。

## RN 实施与验证

应用消费采用当前公开接口；源码维护与定向验证见[任务指引](references/workflows.md)，工程规则从库内 docs/DEVELOPMENT.md 取得。复用同一任务已有且仍适用的依据。

检查命令取当前 package.json/CI；验证公开导出、属性透传、图形与生成一致性，以及实际消费者的颜色、尺寸和无障碍语义。仅查询接口或版本时不自动修改、安装或发布。
