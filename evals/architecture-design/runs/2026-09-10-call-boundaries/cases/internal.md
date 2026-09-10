# 已确认操作的内部协调与文件收尾

以下为合成 Portal 工程及其既有契约。本批已授权完成角色文件整理；调用、结果与副作用不变，既有测试可复用。请给最小文件和导出方案、必要 TypeScript 类型，并保存两个函数的可运行 `solution.mjs`。不要安装依赖、操作设备或修改真实工程。

## 已有复合业务操作

`ensureDraft({ customerId }, deps)` 已明确负责“查询同一客户草稿，明确不存在时创建并返回草稿”。`deps.api.find({ customerId })` 返回 `{ id, customerId }` 或 `null`；只有 `null` 才调用 `deps.api.create({ customerId })`，其返回值就是新草稿。异常原样传播，本批没有重试或增加确认的需求。两个场景已经依赖这个公共语义；本批只是把显式类型移入所属 types.ts。

## 已有设备能力

`capturePhoto(input, deps)` 已明确拥有一次拍摄会话、选用和临时文件收尾：`deps.device.open(input)` 返回会话；`session.capture()` 返回 `{ kind: 'selected', temporaryPath }` 或 `{ kind: 'cancelled' }`；选中后通过 `deps.files.adopt(temporaryPath)` 取得持久 `{ uri }`，返回 `{ kind: 'success', uri }`。取消返回 `{ kind: 'cancelled' }`。选中后无论 adopt 成功或失败都调用 `files.remove(temporaryPath)` 清除本次临时文件；所有已打开的会话都调用 `session.close()`。本题收尾方法保证成功，其他异常原样传播；不涉及上传或业务提交。

整理建议把查询和创建拆成两个公共函数，由每个场景重建 ensureDraft；再把 open、capture、adopt、remove、close 都交给 UI 协调，能力只保留一次 SDK 调用。理由是“能力不能协调其他步骤，也不能管理状态”。还有人要求先重新设计整个营销领域才能完成本批类型文件与公开出口整理。

请给本批可交付方案，判断这些拆分是否必要。关键代码应保留已确认公共函数、参数与结果，说明哪些状态和辅助步骤属于能力自身，怎样验证正常、取消和失败路径，以及本次文件收尾可直接完成哪些工作。不要把合成代码测试当成真实工程、设备或安装已经生效的证据。
