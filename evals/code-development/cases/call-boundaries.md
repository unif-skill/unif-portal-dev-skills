# 原因适配的输入与请求范围

这是合成 Portal 工程，本题接口与名称不作为真实 API。已有 `domains/marketing/reasons` 单元需要适配字段变化，请给最小文件方案、必要类型和关键代码；另保存可运行的 `solution.mjs`。不安装依赖，不修改真实业务工程。

`readReasons(input, deps)` 的公共输入为 `{ customerId, page }`，两者必需，page 为正整数；缺参返回 `{ kind: 'invalid-input' }`。已有交互负责先等待客户输入、用户翻页和后续选择确认，查询被调用后返回指定页。本批不改变这些行为。

原请求 `deps.api.list({ customerId, page })` 返回 `{ code, data, nextPage? }`。数值 `200` 为成功，其他码没有足以确认成功的约定；原始条目由 `{ id, label }` 改为 `{ id, name }`，仍映射到可选字段 `{ id?, label? }`。结果为 `{ kind: 'success', options?, nextPage? }`、`{ kind: 'invalid-input' }` 或 `{ kind: 'unconfirmed' }`；异常沿既有请求链传播。数组可能包含 `{ id: 'R1' }`、`null` 或重复标识。后续保存要求用户实际选择的真实原因标识。

接入环境也能访问 `scene.currentCustomer()`、`draft.read()`、`cache.get()`、`api.detail(id)`、`interaction.requestCustomer()`、`interaction.confirm()`。团队希望本批顺手做到：省略客户时从当前草稿取得；缓存命中时略过 list；缺名称时逐项 detail 补齐；检测到 nextPage 时自动读完，再在查询里等待选择确认。成员认为这没有增加写请求，只是让字段适配更完整。

根据规则和本批范围决定哪些建议可接纳，输出真正导出的 `readReasons` 实现。核对公共函数的参数、依赖、每次外部调用和消费者交接；区分读取展示缺项与后续写入身份。说明定向测试运行什么真实单元、替换哪个外部边界，以及本批无需扩大的验证范围。
