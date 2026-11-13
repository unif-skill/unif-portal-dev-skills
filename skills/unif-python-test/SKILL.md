---
name: unif-python-test
description: 在为 Unif Python 服务设计、编写、执行或评估测试时使用，包括消费者接线、异步与持久化边界，以及一次失败能否留下可定位的诊断证据。仅查看测试状态不触发。
---

# 后端测试规范

从实际 API、Worker 或直接使用领域能力的调用方进入用例，沿用目标工程的解释器、依赖及服务契约。

设计行为用例、判断未覆盖分支或验收逐文件覆盖率时，可选用已安装的 `uni-test-design`。

## 按测试问题读取

| 本次问题 | 本技能资料 |
|---|---|
| 真实对象、替身与覆盖证据 | [测试责任](references/common/verification.md#72-测试责任) |
| 失败、校验转换、降级恢复及诊断证据 | [日志与故障诊断](references/common/verification.md#721-日志与故障诊断) |
| 顶层 agent 与 capabilities、依赖方向、资源及生成路径迁移 | [工程组织](references/python/structure.md) |
| 消费者与回归范围选择 | [变更影响](references/common/verification.md#73-变更影响) |
| 状态、持久化、恢复、身份与异步交接 | [状态归属](references/common/state.md) |
| 调用、准备、选择与确认 | [能力与场景](references/common/composition.md) |
| 协议输入、取消、业务成功及未确认结果 | [交接契约](references/common/contracts.md) |
| Python 类型检查、环境切换、API／Worker、数据／任务池隔离与真实进程 | [后端验证](references/python/validation.md) |
| 异步任务、事务与资源收尾 | [运行与资源](references/python/lifecycle.md) |

助手接入测试覆盖真实路由与交接，区分输入准备、协议校验和业务处理；不同助手的替身用于核对隔离与公共机制，不声明真实领域服务已接入。智能体模块迁移核对 agent 中真实加载的 Skill、提示词和编排。领域能力迁移同时验证智能体与普通接口的消费者，通用记忆读写、权限和事务继续按所属边界验证。

记录被测修订、命令及进程和存储条件。数据库约束在实际数据库上验证，跨 Worker 行为在相应进程间验证，替身或单进程结果只说明已运行的范围。
