---
name: unif-icons
description: 在查询、使用、维护或排查 @unif/react-native-icons、@unif/harmony-icons 的图标，或调整唯一 SVG／命名源及两端生成产物时使用。
metadata:
  package: "@unif/react-native-icons"
  harmony_package: "@unif/harmony-icons"
---

# Unif Icons

原生鸿蒙图标的图形源、生成与公开导出见[鸿蒙契约与实际库入口](references/harmony.md)。

## React Native

按锁定版本的包导出和公开类型核对下列资料。本地文档位于 `website/docs`，线上文档的构建版本见[官网索引](https://unif-design.github.io/react-native-icons/llms.txt)。

| 任务 | 使用资料 |
|---|---|
| 安装、导入与宿主依赖 | [getting-started](https://unif-design.github.io/react-native-icons/md/getting-started.md) |
| 图标 props 与可访问性 | [api](https://unif-design.github.io/react-native-icons/md/api.md) |
| 新增图形源与生成流程 | [contributing](https://unif-design.github.io/react-native-icons/md/contributing.md) |

## RN 使用边界

应用消费已有图标时从实际版本的公开出口选择名称与风格，使用 size、color 等公开属性；颜色由消费者提供，图标不隐式读取 Design 主题。操作按钮的可访问名称由实际承载者提供，独立表达语义的图标按 API 设置。

图形或命名变化从唯一 SVG 源和清单修改，生成与校验流程见[任务指引](references/workflows.md)。平台参数、渲染及可访问性分别核验，资源生成不能替代行为迁移；普通消费无需运行生成器或引入 SVG transformer。
