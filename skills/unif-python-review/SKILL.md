---
name: unif-python-review
description: 在 Unif Agent、Marketing 等 Python 后端中对明确代码或服务配置变更进行缺陷、契约符合性和工程规范审查时使用。为回答事实问题而查阅源码不单独触发。
---

# 后端审查规范

先核对最新已确认需求、明确排除项及已撤回结论，再对照当前实现与消费者审查本次变化；接续任务、新会话和独立审查都沿用该范围。独立审查复核证据，不重新推定需求；已读且仍适用的依据直接复用。

## 按变化读取

按表中主题与章节取得本次变化需要的依据。

| 本次变化 | 本技能资料 |
|---|---|
| 授权范围、职责与场景交接 | [设计依据](references/common/scope.md)、[职责](references/common/responsibilities.md)、[调用与组合](references/common/composition.md) |
| 状态、身份、异步收尾和资源 | [状态归属](references/common/state.md) |
| 公共输入输出、协议与业务结果 | [交接契约](references/common/contracts.md) |
| 测试证据、消费者与回归范围 | [测试责任](references/common/verification.md#72-测试责任)、[变更影响](references/common/verification.md#73-变更影响) |
| 新增或改变的失败路径 | [日志与故障诊断](references/common/verification.md#721-日志与故障诊断) |
| 六层目录、能力分组、公共入口与服务配置归属 | [工程组织](references/python/structure.md) |
| 异步任务、事务与资源收尾 | [运行与事务](references/python/lifecycle.md) |
| 同源契约、环境隔离及真实进程证据 | [契约与验证](references/python/validation.md) |

工程指定了规则修订时采用该修订。具体业务、库 API 与 SDK 契约从工程入口和实际公开资料取得，不把模板、评测样例或偏好当成新增需求。后端任务、事务、进程与持久化按实际执行层级核对；内存替身不能证明数据库约束，单进程验证不能证明多进程行为。

## 输出

沿实际请求、任务或启动入口核对复用依据、状态所有者和消费者，识别同职责重复逻辑及遗漏的调用迁移、失效实现清理；保留有效契约中的服务与生命周期差异。核对新增或改变的失败路径是否可诊断，原因是否在包装或抑制时丢失、敏感数据是否泄露，原权限、身份、取消、事务和资源保护是否有效。共享源码检查真实运行入口和消费者。

只报告有证据的问题，说明位置、触发条件、实际影响及对应契约。区分需要修复的实现缺陷与已授权设计变化；假设的新需求列为建议或待确认项，不作为既有实现的阻断缺陷。审查不自动授权修复、提交或发布评论。资料溯源见 references/source.json。
