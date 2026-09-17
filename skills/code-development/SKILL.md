---
name: code-development
description: 在采用 Unif 目标架构的 Portal 客户端或 @unif React Native 库开发、测试、审查与交付代码时使用，包括 Chat、Design 组件及 H5 桥接的实现与接入。
---

# 代码开发规范

先区分客户端接入与库源码维护，再按当前单元、契约与消费者取得企业规则，应用于已有的开发、测试、审查或交付过程。

## 依据

优先采用任务或工程指定的规则版本。以下资料按本次改动选择，不因属于同一技能而全部加载；已有依据足够时不扩读。

客户端工程规则：

- 单元划分、文件组织、作用域、类型与命名：[文件规则](references/file-rules.md)。
- SDK 与公共能力选用、组件和样式复用：[复用规则](references/ui.md)。
- 工具、配置及资源文件：[归属规则](references/utilities-config.md)。
- 公共入口、依赖、基础能力与宿主接线：[依赖规则](references/dependencies.md)。
- 任务范围、状态表定位与实现边界：[开发范围](references/scope.md)。
- 初始化工程与代码归属：[目标目录](references/directory.md)。
- 测试组织、质量、变更影响与交付证据：[测试与验收](references/testing.md)。

库与专项接入：

- 修改 @unif React Native 库的源码、公开接口、依赖或发布产物：[库开发](references/library-development.md)。应用仅消费一个库时不加载库维护流程。
- 开发或接入聊天组件、消息列表、输入区与附件展示：[Chat UI](references/chat-ui.md)。
- 使用或修改 Design 组件、主题字体、组件族与 UI 宿主：[Design 系统](references/design-system.md)。
- 开发或排查 H5 容器、设备消息、文档与授权交接：[H5 桥接](references/h5-bridge.md)。

模块职责、公共契约、调用交接或状态变化，同时使用本插件 architecture-design；已有契约下的等价整理沿用有效设计。该技能不可用时按工程指定规范源核对同一规则，并说明缺少技能；缺少必需规范时明确影响，不用通用流程或旧工程惯例替代。

领域、库及 SDK 契约按需从目标工程取得。专题中的路径相对于工程采用的 unif-platform-architecture 规范根目录，表示外部契约入口，不表示完整契约随技能分发；未明确根目录时先从工程入口定位。生成的客户端主题溯源见 references/source.json，专项资料按所列契约与当前代码核对。

## 应用

按所选规则确定本次单元及实际消费者；新增自有适配先按复用规则核实已有公开能力与实际缺口，再核对文件角色、公开出口、运行期归属、契约同源及实际接线。测试与审查覆盖受影响的消费者，交付依据工程配置和真实验证证据；本技能不编排任务、审查轮次或 Git 操作。
