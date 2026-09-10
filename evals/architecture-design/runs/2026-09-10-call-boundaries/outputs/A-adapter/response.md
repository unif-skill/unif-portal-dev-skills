# 本批结论

本批仅在已有 `domains/marketing/reasons` 内将原始条目的 `name` 映射为公共 `label`，保持 `readReasons(input, deps)` 的指定页查询契约。使用了所给 A 版 portal-development 的文件、依赖与定向验证主题，以及 architecture-design 的范围、交接、组合与独立验证主题。题目给出的行为与接口是本次依据；未检查真实工程。

团队提出的五项扩展均不纳入本批。没有写请求不代表没有行为变化：

| 建议 | 本批判断及原因 |
| --- | --- |
| 缺客户时读当前草稿，或读 `scene.currentCustomer()` | 不接纳。公共输入必需；改为隐式状态读取会改变输入来源，并让查询依赖场景状态。 |
| 缓存命中跳过 list | 不接纳。改变实际请求次数与数据来源，需要另行确认缓存及新鲜度契约。 |
| 缺名称时逐项 detail | 不接纳。展示缺项按空处理；新增逐行请求改变调用次数与等待时间，不属于改名。 |
| 有 nextPage 就自动读完 | 不接纳。改变指定页的结果范围、请求次数和用户翻页行为。 |
| 查询里等待选择确认 | 不接纳。输入等待、翻页、选择和确认已有交互负责；查询返回即可。 |

## 公共边界与交接

- 参数仅为显式的 `customerId` 和正整数 `page`。本实现按题目中的字符串标识表示客户与原因 ID；客户空串或全空白表示未提供，输入不作字符串转换、默认页填充或客户替换。有效客户值原样传给 list。
- 必要依赖只有 `deps.api.list`。缺参或页码无效返回 `invalid-input`，外部调用数为 0；有效输入仅一次 `deps.api.list({ customerId, page })`，包括未确认响应和抛异常的情况。
- 精确的数值 `200` 返回 `success`；`'200'`、缺码及其他码均为 `unconfirmed`，不推断确定业务失败。传输异常不捕获改写，沿既有请求链传播。
- 成功时，实际数组按原长度和顺序映射；`null` 映射为 `{}`，`{ id: 'R1' }` 映射为 `{ id: 'R1' }`，重复 ID 保留。只读取实际字符串字段，不采用旧 `label` 补新 `name`，也不生成标识或缺项统计。
- `data: []` 返回 `options: []`，表示本页实际没有记录；缺少或不可读取的列表返回 `{ kind: 'success' }`，消费者显示暂无列表数据，不能声称业务没有匹配。缺少展示数据不改变成功分类。实际提供的有效正整数 `nextPage` 原样交给消费者，不触发后续调用。
- 已有交互先取得客户，再传页码查询；消费者展示返回的可选字段，并依据用户翻页动作再次查询。选择和确认仍由其所属交互或场景完成；消费者无需识别原始业务码。
- 后续保存需要用户实际选中的真实原因 ID。`id` 是可选读取字段，不等于已具备写入参数。缺 ID 或空 ID 的展示行不能作为有效保存输入；不能用展示空串、名称、数组索引、虚构默认值或另一行的 ID 补齐。已有真实 ID 而名称缺失，仍保留该 ID；能否提交由用户的实际选择及保存契约判断。重复 ID 不去重，也不推断用户已经选中某条原因。

## 最小文件与类型方案

在已有单元对应文件内修改，实际角色文件存在则复用；以下为合成工程的拟定落点，不是已修改真实工程：

| 文件 | 内容 |
| --- | --- |
| `domains/marketing/reasons/readReasons.ts` | 保持公共函数名；请求、严格码判断、普通私有映射函数。无需新增服务类或适配框架。 |
| `domains/marketing/reasons/types.ts` | 公共输入、读取视图、结果联合；单元内部原始协议和最小依赖类型。 |
| `domains/marketing/reasons/constants.ts` | 原始接口已约定的 `REASONS_SUCCESS_CODE = 200`，若已有该码常量则复用。 |
| `domains/marketing/reasons/index.ts` | 保持 `readReasons` 及消费者实际需要的公共类型出口；不公开私有映射和原始 DTO。 |
| `__tests__/domains/marketing/reasons/readReasons.test.ts` | 对应公共函数及适配行为的定向测试。 |

必要 TypeScript 类型如下；没有可执行 Schema 或生成源的题目依据，不新增框架或复制 Schema：

```ts
interface ReadReasonsInput {
  customerId: string;
  page: number; // 运行时要求正整数
}

interface ReasonOption {
  id?: string;
  label?: string;
}

interface ReadReasonsSuccess {
  kind: 'success';
  options?: ReasonOption[];
  nextPage?: number;
}

interface ReadReasonsInvalidInput {
  kind: 'invalid-input';
}

interface ReadReasonsUnconfirmed {
  kind: 'unconfirmed';
}

type ReadReasonsResult =
  | ReadReasonsSuccess
  | ReadReasonsInvalidInput
  | ReadReasonsUnconfirmed;

// 原始协议描述接口应提供的字段；运行时不能用它拒绝缺字段行。
interface RawReason {
  id: string;
  name: string;
}

interface RawReasonsResponse {
  code: number;
  data: RawReason[];
  nextPage?: number;
}

interface ReasonsApi {
  // 网络数据进入该边界时尚未可信；实现按实际用途读取。
  list(input: ReadReasonsInput): Promise<unknown>;
}

interface ReadReasonsDeps {
  api: ReasonsApi;
}
```

`solution.mjs` 是可直接由 Node.js 导入的真实具名导出实现，执行上述校验、请求与映射。为独立运行，常量和私有辅助函数同置在该交付文件中；工程落地时按上述现有单元的文件角色放置。实现不读取草稿、场景、缓存，也不调用 detail、补客户或确认。

## 验证证据与范围

已实际使用 Node.js 内置 `node:test` 和 `node:assert/strict`，通过 `node --input-type=module` 导入本次 `solution.mjs` 运行 7 组测试，全部通过，失败 0、跳过 0。真实被测单元是导出的 `readReasons`；仅把网络外部边界 `deps.api.list` 替换为记录请求和返回给定响应的实现。额外环境能力均配置为一旦调用即抛错，真实函数没有被替换。

已覆盖：缺参与非法页码不请求；参数原样传递且忽略无关字段；指定页只请求一次并返回 nextPage；`name → label`；缺项、null、重复与顺序及原数据不被修改；空数组与列表缺失区别；严格数值业务码和缺码；不回退旧 label、不合成身份；异常对象原样传播且不重试。

未执行真实 Portal 类型检查、Jest、消费者源码引用分析、网络联调或 CI。本题未提供这些工程内容，不能把独立函数验证描述为工程已接入。

落地时拟核对单元公开入口及直接消费者的类型引用，运行该真实查询单元和原始协议映射的定向测试；消费者交接有必要补充时，运行真实消费流程，替换 list 外部边界，检查可选展示、用户选中真实 ID 才形成保存输入及缺 ID 不提交。原始接口新字段的必要联调用于确认实际协议，不能用本次 stub 证明。

本批公共结果语义、选择确认、状态、设备及模型任务均未改变，无需因此重跑全部页面、整个营销领域、模型评测或真机验证。只有确认改变公共契约、缓存来源、分页范围、交互或状态，或引用分析无法确定消费者时，才扩大到受影响组合或领域；未来合并与发布仍须执行真实工程配置要求的完整门禁。
