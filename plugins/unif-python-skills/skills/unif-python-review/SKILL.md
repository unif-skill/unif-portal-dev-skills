---
name: unif-python-review
description: 在审查 Unif Python 代码或服务配置的正确性、契约、状态与资源责任、故障证据和验证范围时使用。仅为回答事实问题阅读源码不触发。
---

# 后端审查规范

文中用代码标出的公共主题路径从 `$unif-platform-rules` 读取。

沿变更的请求、任务或启动入口核对服务配置、事务边界与真实消费者。

## 按变化读取

| 本次变化 | 本技能资料 |
|---|---|
| 方案前提、已确认的范围与取舍、职责及场景交接 | 设计依据（`references/architecture/scope.md#11-设计依据与适用范围`）、职责（`references/architecture/responsibilities.md`）、调用与组合（`references/architecture/composition.md`） |
| 状态、身份、异步收尾和资源 | 状态归属（`references/architecture/state.md`） |
| 公共输入输出、协议与业务结果 | 交接契约（`references/architecture/contracts.md`） |
| 协议、字段或数据库定义退役 | `$unif-platform-rules` 的“契约变更与清理”，核对跨仓消费者、生成物与初始化 SQL |
| 测试证据、消费者与回归范围 | 测试责任（`references/architecture/verification.md#72-测试责任`）、变更影响（`references/architecture/verification.md#73-变更影响`） |
| 外部调用、校验转换、失败抑制和恢复路径的诊断 | 日志与故障诊断（`references/architecture/verification.md#721-日志与故障诊断`） |
| 顶层 agent 与 capabilities、公共入口与服务配置归属 | [工程组织](../unif-python-dev/references/python/structure.md) |
| 异步任务、事务与资源收尾 | [运行与事务](../unif-python-dev/references/python/lifecycle.md) |
| BasedPyright、同源契约、环境隔离及真实进程证据 | [契约与验证](../unif-python-dev/references/python/validation.md) |

助手接入审查核对 Agent 对应 capabilities 中的专属能力说明、输入投影和协议处理。接入层保留协议识别与交接所需的领域信息，业务决策与领域流程由所属业务服务承担。智能体自身的 Skill、提示词与编排归顶层 agent，Marketing 的业务规则与校验归 capabilities，普通接口继续消费所属公开能力。通用 memory 的读写、权限和事务按服务与持久化职责审查，模块归属由实际责任决定。

每项发现给出位置、触发条件、服务契约和具体影响。核对实际进程与持久化条件，区分内存替身、数据库约束及多进程证据。
