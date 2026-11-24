---
name: unif-python-service
description: 在 Unif Agent、Marketing 等 Python 服务中，需要核对助手路由、领域能力、Worker 隔离、数据库事务或服务诊断时使用。仅解释已给出的配置值、版本或接口事实，不涉及实现核对时不使用。
---

# Unif Python 服务

从出问题或发生变化的 API、Worker、启动命令或领域接口进入，找到它实际调用的服务和数据库。[工程范围](references/python/scope.md)用于确定这次要核对的仓库与修订。

## 确认助手、领域和通用服务各自负责什么

Agent 工程的 `agent/` 和 `capabilities/` 位于服务包根目录下，彼此同级。`agent/` 装配 Skill、提示词、工具和任务编排。`capabilities/<助手名>/` 保存该助手的能力说明，负责协议校验和交接。

Marketing 工程的 `capabilities/<业务域>/` 拥有相应领域的规则，供智能体和普通 HTTP 接口共同调用。通用 memory 的读写、权限和事务由相应服务管理。[目录与依赖](references/python/structure.md)

助手接入变化时，从真实路由检查输入从哪来、谁校验、谁采用结果，并验证未知或未授权助手的处理。使用第二个助手替身可以检验选择和隔离；确认该助手已经提供真实业务，需要对应服务的证据。移动模块后还要核对最终装配文本、资源导入、子进程命令和镜像内路径。

## 按实际进程核对事务和运行环境

跟到持有连接、事务或任务的组件，查看正常返回、异常和取消时分别怎样收尾。进程内锁只约束同一进程。验证多个 Worker 的业务唯一性时，使用对应的进程、数据库约束和真实记录，保留已有数据。[运行与资源](references/python/lifecycle.md)

环境切换要核对 API 和 Worker 实际连接的 MySQL、Redis、命名空间以及 Worker 注册。验证 HTTP／SSE 和任务交接时，写明运行了哪些进程、采用了哪些替身、实际收到什么结果。[契约与验证](references/python/validation.md)

修改 Python 源码时使用目标解释器和锁定依赖执行 BasedPyright。沿用工程配置，无配置时使用 `recommended`。服务出错时，核对日志是否能从一次失败追到所属调用、异常原因与安全的关联字段。公共诊断责任见 `$unif-platform-rules` 的 `references/architecture/verification.md#721-日志与故障诊断`，身份和回执分别见 `references/architecture/state.md` 与 `references/architecture/contracts.md`。

## 按任务选择工程方法

| 当前任务 | 方法入口 |
|---|---|
| 修改助手接入、Worker 或领域服务 | `uni-code-change` |
| 排查实际请求、进程或事务故障 | `uni-debugging` |
| 审查服务代码和配置差异 | `uni-code-review` |
| 设计路由、事务和持久化用例 | `uni-test-design` |
| 选择并运行本次服务验收检查 | `uni-verify-change` |
| 实施或审查已确定的跨仓协议变更 | `unif-contract-change` |
