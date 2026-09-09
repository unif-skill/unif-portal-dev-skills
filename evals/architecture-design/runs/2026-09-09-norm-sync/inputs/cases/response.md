# 查询展示与业务写入审查

以下端点、签名和响应是独立题设，不是实际工程 API。依据所附平台规范审查草案，给出最小的类型调整、逐个响应的处理和必要验收；只写设计结论，不实现产品代码。

## 题设契约与响应

营销端点已确认只认数值 `code: 200` 为接口成功，数值 `403` 为权限拒绝；其他码值及字符串码未确认。完成拜访的写请求必须有实际的 `visitTaskId`、`customerId`；保存原因还需要用户选择的 `reasonId`。下列响应分别独立发生：

1. 任务查询返回 `{ code: 200, data: { items: [ { task: { visitTaskId: "V1" }, customer: { customerId: "C1" }, address: { city: "杭州" } }, { task: { phase: "visiting" }, customer: { customerName: "店乙" }, address: { street: "二号路" } }, null ] } }`。列表展示任务状态、客户名和地址，点击后才准备业务写入。
2. 同一查询分别返回 `{ code: 200, data: { items: [] } }` 和 `{ code: 200, data: {} }`。
3. 保存原因返回 `{ code: 200, data: false }`。此端点的已定含义是：接口成功后，只有 `data === true` 才满足继续完成拜访的条件。
4. 已发送的一次创建请求返回 `{ code: 200, data: {} }`，没有记录编号；后续读取详情需要真实编号。
5. 查询返回 `{ data: { items: [] } }`；写请求超时；写响应为 `{ code: "200", data: { id: "N1" } }`。
6. 另一个领域的查询端点已确认以字符串 `code: "OK"` 表示成功，`data: 0` 是有效统计值。

## 待审查草案

后端原始类型按其应提供的完整数据定义。开发者计划用同一完整对象 Schema 校验整页，把缺值行移除并增加异常计数；缺少列表时返回空数组。读取视图写为：

```ts
interface TaskRow {
  task?: { visitTaskId: string; phase: string };
  customer?: { customerId: string; customerName: string };
  address?: { city: string; street: string };
}
```

方案说明说“字段缺失仍展示”，认为只把外层对象设成可选已经足够。为了让所有行都能进入完成流程，计划给缺失 ID 填列表索引。创建成功但编号缺失时增加 `success_receipt_invalid`，自动再创建一次。公共传输层拟统一只接受数值 `200`。

请说明哪些处理成立、哪些应调整，并给出读取视图与写入输入的最小 TypeScript 示例。保留题设规定的业务语义，不补造其他接口或码表。
