---
name: unif-python-review
description: 在审查 Unif Python 代码或服务配置的正确性、契约、状态与资源责任、故障证据和验证范围时使用。仅为回答事实问题阅读源码不触发。
---

# 后端审查规范

文中用代码标出的公共主题路径从 `$unif-platform-rules` 读取。

沿变更的请求、任务或启动入口核对服务配置、事务边界与真实消费者。

审查兼容用例、事件顺序或覆盖率结论时，可选用已安装的 `uni-test-design` 核对判据。

## 按变化读取

| 本次变化 | 本技能资料 |
|---|---|
| 方案前提、已确认的范围与取舍、职责及场景交接 | 设计依据（`references/architecture/scope.md#11-设计依据与适用范围`）、职责（`references/architecture/responsibilities.md`）、调用与组合（`references/architecture/composition.md`） |
| 状态、身份、异步收尾和资源 | 状态归属（`references/architecture/state.md`） |
| 公共输入输出、协议与业务结果 | 交接契约（`references/architecture/contracts.md`） |
| 测试证据、消费者与回归范围 | 测试责任（`references/architecture/verification.md#72-测试责任`）、变更影响（`references/architecture/verification.md#73-变更影响`） |
| 外部调用、校验转换、失败抑制和恢复路径的诊断 | 日志与故障诊断（`references/architecture/verification.md#721-日志与故障诊断`） |
| 顶层 agent 与 capabilities、公共入口与服务配置归属 | [工程组织](../unif-python-dev/references/python/structure.md) |
| 异步任务、事务与资源收尾 | [运行与事务](../unif-python-dev/references/python/lifecycle.md) |
| BasedPyright、同源契约、环境隔离及真实进程证据 | [契约与验证](../unif-python-dev/references/python/validation.md) |

涉及助手接入时，核对专属能力说明、输入投影和协议处理是否集中在 Agent 对应的 capabilities 单元；区分必要的领域接入认知与业务决策，不以删除所有业务名称代替边界审查，也不允许适配器承接领域业务流程。智能体自身的 Skill、提示词与编排归顶层 agent，Marketing 的业务规则与校验归 capabilities。核对普通接口仍可使用所属能力，通用 memory 的读写、权限与事务未因名称迁入 agent。

每项发现给出位置、触发条件、服务契约和具体影响。核对实际进程与持久化条件，区分内存替身、数据库约束及多进程证据。
