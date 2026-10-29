---
name: unif-icons
description: 在消费、维护或排查 @unif/react-native-icons，或维护其 SVG／命名源与 RN／鸿蒙生成产物时使用。不用于原生鸿蒙组件 API 接入。
metadata:
  package: "@unif/react-native-icons"
---

# Unif Icons

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-icons/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

原生鸿蒙组件接入与手写实现使用 code-development 的 harmony-icons 专题；本技能在跨端任务中负责取得共享图形源和生成依据。

## 按任务读取

本地源码的使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读当前任务相关单页，全文是确需全局资料时的选项。

| 任务 | 使用资料 |
|---|---|
| 安装、导入与宿主依赖 | [getting-started](https://unif-design.github.io/react-native-icons/md/getting-started.md) |
| 图标 props 与可访问性 | [api](https://unif-design.github.io/react-native-icons/md/api.md) |
| 新增图形源与生成流程 | [contributing](https://unif-design.github.io/react-native-icons/md/contributing.md) |

## 使用边界

应用消费已有图标时从实际版本的公开出口选择名称与风格，使用 size、color 等公开属性；颜色由消费者提供，图标不隐式读取 Design 主题。操作按钮的可访问名称由实际承载者提供，独立表达语义的图标按 API 设置。

图形或命名变化从唯一 SVG 源和清单修改，按库文档识别已采用的 RN／鸿蒙生成目标，更新并校验实际产物。保留 SVG 校验、几何与绘制语义；实际存在的 Outlined/Filled 风格分别命名。平台参数、渲染或可访问性变化按各自契约核对，不能靠资源生成代替实现。应用消费已有图标无需运行生成器或引入 SVG transformer。

## 实施与验证

本技能可单独使用，完整操作和维护依据见[任务指引](references/workflows.md)。应用消费采用公开接口和已有能力；源码维护从库内 docs/DEVELOPMENT.md 取得工程指定的规范。工程已配置共用阶段技能时按需使用，无需为本技能另行安装。复用同一任务已取得的有效依据。

验证实际输入、事件、结果与消费者，保留本库取消、错误和资源保护；检查命令从当前 package.json/CI 取得。只查询接口或版本时回答已核实事实，不自动修改代码、安装依赖或执行发布。
