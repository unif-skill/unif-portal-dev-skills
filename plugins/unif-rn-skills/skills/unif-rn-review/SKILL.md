---
name: unif-rn-review
description: 在 Unif React Native 客户端、@unif/react-native-* 库或其共享核心中对明确代码或构建配置变更进行缺陷、契约符合性和工程规范审查时使用。为回答事实问题而查阅源码不单独触发。
---

# RN 审查规范

按最新目标、有效契约和实际消费者独立核实本次方案的前提与影响，不因作者或用户已同意改法就省略核查。发现未确认的偏差或取舍，报告证据、后果和需用户决定的部分，不擅自否决或替换产品选择。用户知情确认的变更按新决定审查，无实质疑点不追加确认；排除项、撤回意见及仍适用的依据继续沿用。

## 按变化读取

按表中主题与章节取得本次变化需要的依据。

| 本次变化 | 本技能资料与工程依据 |
|---|---|
| 授权范围、职责与场景交接 | [设计依据](references/common/scope.md)、[职责](references/common/responsibilities.md)、[调用与组合](references/common/composition.md) |
| 状态、身份、异步收尾和资源 | [状态归属](references/common/state.md) |
| 公共输入输出、协议与业务结果 | [交接契约](references/common/contracts.md) |
| 测试证据、消费者与回归范围 | [测试责任](references/common/verification.md#72-测试责任)、[变更影响](references/common/verification.md#73-变更影响) |
| 新增或改变的失败路径 | [日志与故障诊断](references/common/verification.md#721-日志与故障诊断) |
| Portal 环境文件复用、构建选择与加载一致性 | [文件规则](references/rn/file-rules.md)、[验证](references/rn/testing.md) |
| Portal 文件、公开入口与代码归属 | [范围](references/rn/scope.md)、[文件](references/rn/file-rules.md)；归属不清时补[目录](references/rn/directory.md)与[配置](references/rn/utilities-config.md) |
| Portal 组件、样式与公共能力组合 | [UI](references/rn/ui.md)、[依赖](references/rn/dependencies.md) |
| Portal 消费者、宿主与平台接线 | [验证](references/rn/testing.md)，按涉及接线补[依赖](references/rn/dependencies.md) |
| @unif RN 库与共享核心 | 本库 AGENTS.md、开发说明、采用记录及公开契约；共同规则按上表选读 |

工程指定了规则修订时采用该修订。具体业务、库 API 与 SDK 契约从工程入口和实际公开资料取得，不把模板、评测样例或偏好当成新增需求。RN 的组件、适配、实际消费者与所影响的 iOS、Android 或 Web 接线分别核对。

## 输出

沿实际入口核对复用依据、状态所有者和消费者，识别同职责重复逻辑及遗漏的调用迁移、失效实现清理；保留有效契约中的场景与平台差异。核对新增或改变的失败路径是否可诊断，原因是否在包装或抑制时丢失、敏感数据是否泄露，原权限、身份、取消、事务和资源保护是否有效。共享源码检查真实产物和消费者；单端验证不替代其他目标。

只报告有证据的问题，说明位置、触发条件、实际影响及对应契约。区分需要修复的实现缺陷与已授权设计变化；假设的新需求列为建议或待确认项，不作为既有实现的阻断缺陷。审查不自动授权修复、提交或发布评论。资料溯源见 references/source.json。
