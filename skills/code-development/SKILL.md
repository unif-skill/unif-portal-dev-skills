---
name: code-development
description: 在采用 Unif 目标架构的 Portal 客户端或 @unif React Native 库新建工程、实现或调整代码、接入能力、定位实现缺陷，或开发库文档站、组件 Web 示例与 LiveDemo 时使用。单纯查询版本、解释已有接口或读取状态不触发。
---

# 代码开发规范

先区分客户端接入与库源码维护，再按当前单元、契约与消费者取得实现依据。测试、审查和交付使用各自入口；它们可以按需取得本技能的工程规范，不因此启动开发工作。

## 依据

优先采用任务或工程指定的规则版本。同一上下文中已读、版本适用且覆盖当前判断的规则和契约直接复用；范围或来源变化时只补相关部分。以下资料按需选择，不因属于同一技能而全部加载。

客户端工程规则：

- 单元划分、文件组织、作用域、类型与命名：[文件规则](references/file-rules.md)。
- SDK 与公共能力选用、组件和样式复用：[复用规则](references/ui.md)。
- 工具、配置及资源文件：[归属规则](references/utilities-config.md)。
- 公共入口、依赖、基础能力与宿主接线：[依赖规则](references/dependencies.md)。
- 任务范围、状态表定位与实现边界：[开发范围](references/scope.md)。
- 初始化工程与代码归属：[目标目录](references/directory.md)。
- 测试组织、质量、变更影响与交付证据：[测试与验收](references/testing.md)。

库与专项接入：

- 新建或维护 @unif React Native 库的源码、公开接口、依赖或发布产物：[库开发](references/library-development.md)。应用仅消费一个库时不加载库维护流程。
- 新库、工程标准尚未接入，或首次／恢复发布准备：[新库接入](references/library-onboarding.md)。成熟工程的小改动沿用有效接入依据。
- 开发或接入聊天组件、消息列表、输入区与附件展示：[Chat UI](references/chat-ui.md)。
- 使用或修改 Design 组件、主题字体、组件族与 UI 宿主：[Design 系统](references/design-system.md)。
- 开发库文档站、组件 Web 示例、公开演示或 LiveDemo：[文档站开发](references/documentation-site.md)。组件附带 Web 示例也进入此专题；仅改组件内部或原生能力且不影响网站时不加载。
- 开发或排查 H5 容器、设备消息、文档与授权交接：[H5 桥接](references/h5-bridge.md)。

需要确定或实质调整模块职责、公共契约、调用交接或状态归属时，使用本插件 architecture-design。按已有契约实现、排查或整理时沿用有效设计；仅为核对已有规则，不重启架构设计。缺少技能入口时可采用工程指定的同一规范源；缺少必需依据时明确影响，不用通用流程或旧工程惯例替代。

领域、库及 SDK 契约按需从目标工程取得。专题中未另标所属仓库的规范路径相对于工程采用的 unif-platform-architecture 规范根目录；标明组织标准仓或库根目录的路径按该仓定位。它们是外部依据入口，不表示完整契约随技能分发；未明确根目录时先从工程入口定位。生成的客户端主题溯源见 references/source.json，专项资料按所列契约与当前代码核对。

## 应用

确定本次单元及实际消费者。新增自有适配先核实已有公开能力与实际缺口，再核对文件角色、公开出口、运行期归属、契约同源及实际接线。
