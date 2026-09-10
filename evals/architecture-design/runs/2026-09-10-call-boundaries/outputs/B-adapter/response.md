# 原因字段适配结论

本批只接纳原始字段 `name → label` 的确定性映射，沿用 `readReasons({ customerId, page }, deps)` 的输入、单页请求和结果契约。已实现的可运行代码在同目录 `solution.mjs`，具名导出 `readReasons`，无需依赖即可由 Node.js 导入。

依据是所给材料中 architecture-design 的 scope、composition、contracts、verification，以及 portal-development 的文件、依赖和定向验证规则。这里直接采用题目已经确认的契约，不改变既有交互，不另行设计整个营销模块。

| 建议 | 本批决定及原因 |
|---|---|
| 省略客户后读取草稿或当前场景 | 不接纳。`customerId` 必需；缺参返回 `invalid-input`。读取 `draft.read()` 或 `scene.currentCustomer()` 会引入隐式业务状态并改变输入责任。 |
| 缓存命中时跳过 list | 不接纳。会改变每次调用的请求行为及结果来源；是否复用既有结果属于调用方按已确认场景规则做的决定。 |
| 名称缺失后逐项 detail | 不接纳。缺少展示字段不改变成功状态；补查会增加外部读取次数和顺序，已经超出字段映射。 |
| 检测 nextPage 自动读完 | 不接纳。会扩大结果范围并增加请求；本契约只返回输入指定页，分页由已有交互触发。 |
| 查询内等待客户或选择确认 | 不接纳。客户准备发生在调用前；选择与确认发生在返回后，继续由现有交互负责。 |

“没有新增写请求”不足以使这些建议成为等价适配。请求次数、来源、顺序、结果范围和交互责任同样属于契约变化；如未来另有需求，应先确认相应能力或场景契约。

## 参数、依赖及每次调用

- 公共业务输入仍只有必需的 `customerId` 和 `page`；不新增选中项、草稿、场景或确认参数。运行时对空输入、缺失或空字符串客户，以及非正整数 page 返回 `invalid-input`，不读取任何依赖。客户标识不裁剪、不转换、不从其他状态补出；题目未提供客户标识的额外业务合法性规则。
- 依赖面只有 `deps.api.list`。真实应用仍由已有组装处传入该请求链的实现，包括已有认证与传输处理，不添加容器、缓存或新的底层 HTTP 实现。
- 每次合法调用恰好执行一次 `await deps.api.list({ customerId: input.customerId, page: input.page })`。顺序是输入检查、指定页请求、业务码解释、字段投影、返回。没有递归、分页循环、详情请求或交互等待。
- 只有数值 `200` 返回 `success`。`'200'`、其他码或缺码均返回 `unconfirmed`；不会按 HTTP 成功、有 data 或 ID 猜测业务成功。请求抛出的异常原样沿 Promise 传播，不转换成这三个业务结果之一。
- 可读数组逐行映射并保留完整数量、原始顺序和重复标识。`{ id: 'R1' }` 得到 `{ id: 'R1' }`，`null` 得到 `{}`；没有以缺项为理由过滤、去重、拒绝整页或触发补查。字段不存在或为 null 时保持可选字段缺失，保留原始空字符串，不编造名称或身份。
- `code: 200, data: []` 得到 `success` 和 `options: []`；成功但 data 不可读为数组时保留 `success` 并省略 options。前者表示本页无记录，后者只能展示暂无列表数据，不能推断业务无匹配。已有 nextPage 有值时透传，并不据此请求。

## 最小文件与类型方案

保留已有 `domains/marketing/reasons` 单元，不新建服务层或通用转换模块。实际工程文件名未在题目提供，以下是需要对齐到现有文件的最小角色方案，不能视为已核实的真实路径：

| 文件角色 | 本批内容 |
|---|---|
| `domains/marketing/reasons/readReasons.ts` 或已有对应实现 | 原有请求链上改为读取 name，保留单页调用和业务结果解释；局部结果对象属于本次调用。 |
| 该单元已有 `types.ts` | 原始 DTO 字段更新为 name；读取选项 id、label 保持可选；公开输入与结果分支保持原语义。已有生成契约则改源并派生类型，不重复手写。 |
| 该单元已有 `constants.ts` | 复用已有数值成功码常量；若本单元尚无命名码值，定义 `LIST_REASONS_SUCCESS_CODE = 200`，不创建重复全局码表。 |
| 该单元已有 `index.ts` | 继续具名导出 readReasons 及消费者实际需要的公共类型；不导出原始协议、私有辅助。已有出口无变化时无需修改。 |
| `__tests__/domains/marketing/reasons/readReasons.test.ts` 或已有对应测试 | 覆盖真实公共函数、响应适配及调用边界。 |

本批没有独立样式、共享状态或校验框架需求，不补空角色文件。以下给出必要类型形状；题目没有规定 customerId、原因 ID、名称和 nextPage 的原子类型，故示例将这些外部值写成 unknown 并保持实际值，不擅自规定字符串、数字转换或兜底值。实际接入必须沿用所属接口和已确认公共契约的具体类型，不能借 unknown 放宽原有公共类型。`page` 的正整数约束由运行时检查保证。

```ts
export interface ReadReasonsInput {
  customerId: unknown;
  page: number;
}

// 后端应提供的条目结构；wire data 仍需按实际可读情况处理，
// 不能用此接口对成功页做全对象拒绝。
interface RawReasonDto {
  id: unknown;
  name: unknown;
}

interface RawReasonsResponse {
  code?: unknown;
  data?: unknown;
  nextPage?: unknown;
}

export interface ReasonOption {
  id?: unknown;
  label?: unknown;
}
export interface ReadReasonsSuccess {
  kind: 'success';
  options?: ReasonOption[];
  nextPage?: unknown;
}
export interface ReadReasonsInvalidInput {
  kind: 'invalid-input';
}
export interface ReadReasonsUnconfirmed {
  kind: 'unconfirmed';
}
export type ReadReasonsResult =
  | ReadReasonsSuccess
  | ReadReasonsInvalidInput
  | ReadReasonsUnconfirmed;

interface ReasonsApi {
  list(input: ReadReasonsInput): Promise<RawReasonsResponse | null | undefined>;
}
export interface ReadReasonsDependencies {
  api: ReasonsApi;
}
export declare function readReasons(
  input: ReadReasonsInput,
  deps: ReadReasonsDependencies,
): Promise<ReadReasonsResult>;
```

这段是工程接入类型方案；实际函数实现见 `solution.mjs`，不是只声明类型或返回固定结果。异常不会被类型联合误写成已捕获的失败分支。

## 消费者交接

现有交互先取得客户和页码，再调用公开 readReasons；函数返回 success 后，交互以 options 展示本页，并在用户明确翻页时用 nextPage 发起下一次调用。消费者读取功能结果，不自行再解析后端 code 或 name。原始 name 改动留在适配边界，页面仍消费 label。

读取视图允许缺少展示信息与身份。保存链路必须取用户实际选中条目里的真实 `id`，并在后续写入能力的必要输入检查中确认它存在且符合该写入契约；`{ id: 'R1' }` 缺名称不会因此丢失真实身份，但缺 id 的行不能用 label、数组序号、占位文案、另一个条目或随机 ID 补成可保存对象。重复 id 不在读取适配中去重；渲染若需要位置关联，位置仅服务视图，绝不是保存标识。不默认选择第一条，也不在查询内触发选择、确认或保存。

草稿、当前选中项和确认继续由既有交互或场景维护，readReasons 不读取也不写入它们。消费者将结果交给原有选择与确认流程即可；没有依据新增按钮、重试或详情交互。

## 验证证据与范围

已执行：使用 Node.js 的 `node:assert/strict`，直接导入此次输出的真实 `readReasons` 实现，运行 25 个案例并全部通过。没有替换 readReasons 或映射逻辑，只替换其外部 `deps.api.list` 边界，并用 Proxy 使其他依赖访问立即报错。

覆盖了：13 个无效输入零依赖访问；有效输入精确参数与仅一次 list 调用；带 nextPage 时仍不补页；正常项、缺名称、null、缺身份、重复 ID、空名称的保留及顺序；原响应不被修改；4 种不可读列表仍成功且省略 options；空数组仍保留；字符串成功码、其他码、缺码、null 响应为 unconfirmed；同一异常对象原样传播。测试输出为 `25 cases passed against the exported readReasons implementation`。

尚未执行：真实工程类型检查、导入关系与消费者测试、真实 API 联调或 CI；本任务禁止访问实际工程与网络，不能把这次独立实现检查等同为工程接入完成。

实际接入后的定向验证应运行真实 reasons 适配/公共函数测试，替换网络请求边界；确认输出仍满足既有展示、手动翻页和选择保存消费者的契约。必要时运行直接消费者的相关用例，重点验证缺名称仍可展示、缺身份无法构造有效保存请求，以及所选真实 ID 交给原有确认与保存步骤。类型检查和静态引用用于找消费者；如已有 H5 或其他非静态关系，按实际对应关系补齐，不能凭假定宣布不存在。

本批只是原始字段变化，不默认扩展到整个营销领域测试、模型任务评测、真机或原生构建，不要求所有页面重写，也不重复测试后端内部实现。必要联调只核实原始字段与码约定；合并和发布仍遵守实际工程 required CI。只有发现公共语义、请求次数、共享状态、真实消费者关系或平台接线受到影响，才扩大相关组合、领域或集成验证范围。
