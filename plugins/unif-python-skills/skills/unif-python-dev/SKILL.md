---
name: unif-python-dev
description: 在 Unif Agent、Marketing 等 Python 服务实现、修复或重构代码与配置，处理服务接入、异步运行、持久化或故障诊断时使用。仅查询运行状态、版本或既有接口不触发。
---

# 后端代码开发

从真实请求、Worker 或启动入口核实当前契约、调用方与事务影响。沿用已确认的范围，新事实改变原取舍时指出证据和影响。

- 修改范围与现有行为：[实施范围](references/scope.md)；第三方库、框架或 SDK 的设计、接入、封装与排障：[依赖治理](references/common/verification.md#71-依赖治理)，核对官方依据与项目采用条件。
- 智能体指令与编排、领域能力、通用服务的归属见[目录与依赖](references/structure.md)。
- 服务配置、环境变体及启动接线：[目录与依赖](references/structure.md)、[契约与验证](references/validation.md)。
- 异步执行、取消、收尾、事务及调用预算：[运行与资源](references/lifecycle.md)。
- 持久化、身份切换及跨任务资源交接见[状态归属](references/common/state.md)。
- BasedPyright、同源契约、任务指令、消费者接线和验证证据：[契约与验证](references/validation.md)。
- API、模型及持久化失败按[日志与故障诊断](references/common/verification.md#721-日志与故障诊断)核对服务端实际记录。

迁移后对照实际加载的指令、事务与资源路径，核对调用方已接到所属实现。

服务公开结果及跨边界协作按[交接契约](references/common/contracts.md)核对。

修改兼容分支或异步保护需要设计回归时，按项目采用的通用测试规范执行；已安装的 `uni-test-design` 提供相应判据。
