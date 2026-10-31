---
name: backend-review
description: 在 Unif Agent、Marketing 等 Python 后端中对明确代码变更进行缺陷、契约符合性和工程规范审查时使用。为回答事实问题而查阅源码不单独触发。
---

# 后端审查规范

对照有效需求、契约、实际实现与消费者审查本次变化。本目录携带必需的共同与后端规范，不要求安装其他技能。独立审查需取得自身尚未具有的依据；同一上下文已读且仍适用的内容直接复用。

## 按变化读取

| 本次变化 | 本技能资料 |
|---|---|
| 授权范围、职责与场景交接 | [设计依据](references/common/scope.md)、[职责](references/common/responsibilities.md)、[调用与组合](references/common/composition.md) |
| 状态、身份、异步收尾和资源 | [状态归属](references/common/state.md) |
| 公共输入输出、协议与业务结果 | [交接契约](references/common/contracts.md) |
| 验证范围、日志与失败诊断 | [验证与诊断](references/common/verification.md) |
| Python 后端 | [工程组织](references/backend/structure.md)、[运行与事务](references/backend/lifecycle.md)、[契约与验证](references/backend/validation.md) |

工程指定了规则修订时采用该修订。具体业务、库 API 与 SDK 契约从工程入口和实际公开资料取得，不把模板、评测样例或偏好当成新增需求。后端的任务、事务、进程与持久化证据按实际执行层级核对；内存替身不能证明数据库或多进程约束成立。

## 输出

核对新增或改变的失败路径是否可诊断，原因是否在包装或抑制时丢失、敏感数据是否泄露，原权限、身份、取消、事务和资源保护是否有效。共享源码检查真实运行入口和消费者；单进程验证不替代多进程或真实持久化证据。

只报告有证据的问题，说明位置、触发条件、实际影响及对应契约。区分需要修复的实现缺陷与已授权设计变化；审查不自动授权修复、提交或发布评论。资料溯源见 references/source.json。
