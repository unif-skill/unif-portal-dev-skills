本批只接受后端条目 `name → label` 的确定性字段映射，维持 `readReasons({ customerId, page }, deps)` 的公共语义：调用后读取指定客户的指定一页。技能依据为 architecture-design 的 `composition.md`（功能按显式输入执行、场景协调交互）、`contracts.md`（业务成功及缺项映射、请求数量和范围变更）和 `verification.md`，以及 portal-development 的 `file-rules.md`、`testing.md`。这些依据足以处理本题，无需扩大到其他工程或主题。

团队建议均不纳入本批：

| 建议 | 决定与原因 |
| --- | --- |
| 省略客户时读取当前草稿或当前场景 | 不接纳。customerId 必填；缺参返回 invalid-input。查询不读取隐式业务状态补参数。已有交互继续等待用户提供客户。 |
| 缓存命中时跳过 list | 不接纳。是否复用结果由调用方按已确认场景规则决定；本批查询每次有效调用都执行一次 list。 |
| 缺名称时逐项 detail | 不接纳。缺展示字段按空展示；逐项补查改变依赖、请求数量及错误链，需要另行定义能力或场景契约。 |
| 发现 nextPage 后自动读完 | 不接纳。改变请求次数和结果范围；本批只返回当前页与可用的 nextPage，由既有翻页交互决定下一次调用。 |
| 查询中等待选择确认 | 不接纳。选择、确认及后续保存继续由既有交互和场景承担；查询不能替用户选择，也不控制后续流程。 |

这些行为即使只有读请求，也不是等价字段适配。后续若提出明确的新需求，应先定义输入准备、调用触发、结果范围、交互及消费者交接，再安排相应修改。

最小文件方案沿用题目已有 `domains/marketing/reasons` 单元，不创建新公共能力、服务类、缓存或通用转换引擎：

| 文件 | 必要内容 |
| --- | --- |
| `domains/marketing/reasons/readReasons.ts` | 既有公共函数；请求参数校验、一次 list、业务码解释和内部普通函数 toReasonOption。若真实工程已有承载此职责的适配文件，直接修改该文件，不另建同职文件。 |
| `domains/marketing/reasons/types.ts` | 公共输入、读取视图、结果分支及窄依赖接口；原始 DTO 留在此适配单元内部使用。 |
| `domains/marketing/reasons/constants.ts` | `LIST_REASONS_SUCCESS_CODE = 200`，业务成功码具备固定契约含义。 |
| 既有 `domains/marketing/reasons/index.ts` | 保持具名导出 readReasons 及实际公共类型；不导出内部映射函数、原始 DTO 或码常量。名称和调用签名不变，无需为了后端改名让消费者改用 name。 |
| `__tests__/domains/marketing/reasons/readReasons.test.ts` | 对真实公共函数做定向测试；按目标工程现有源码与测试根目录补齐实际前缀。 |

没有样式、共享状态或 Schema 框架需求，不补空角色文件。此文件表是合成题目的落地方案；未读取真实工程，因此不宣称已经确认其现有文件名、引用关系或接线。

必要类型如下。字符串标识不做数值转换或 trim 改写；客户必须为非空字符串。页码为正整数，nextPage 只有可作为同一 page 输入时才向消费者提供。原始 DTO 描述接口应提供的字段，边界接收 unknown 并逐字段安全读取，以容纳题目中实际出现的缺项；不能用原始 DTO 的完整性拒绝整页。

```ts
// types.ts
export interface ReadReasonsInput {
  customerId: string;
  page: number;
}

export interface ReasonOption {
  id?: string;
  label?: string;
}

export interface ReadReasonsSuccess {
  kind: 'success';
  options?: ReasonOption[];
  nextPage?: number;
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

export interface ReasonsApi {
  list(input: ReadReasonsInput): Promise<unknown>;
}

export interface ReadReasonsDeps {
  api: ReasonsApi;
}

// 仅供适配单元使用，不从公共 index.ts 导出。
export interface RawReasonDto {
  id: string;
  name: string;
}

export interface RawReasonsResponse {
  code: number;
  data: RawReasonDto[];
  nextPage?: number;
}

// readReasons.ts 的公共签名
export async function readReasons(
  input: ReadReasonsInput,
  deps: ReadReasonsDeps,
): Promise<ReadReasonsResult>;
```

`solution.mjs` 是对应的完整可执行实现，真正具名导出 readReasons；为满足独立 Node.js 导入要求，命名常量和私有映射函数与其放在同一个交付文件中。运行时仍防御缺参和不合类型的输入，不依赖 TypeScript 调用方一定正确。

调用与交接逐项核对：

- 输入不完整或无效时，返回 `{ kind: 'invalid-input' }`，不触碰任何外部依赖。
- 输入有效时，只调用一次 `deps.api.list({ customerId, page })`；原样传递已给出的客户和页码，不传入多余输入字段。依赖接口仅含 api.list，不含 scene、draft、cache、detail 或 interaction。
- 仅数值 `200` 映射为 success。字符串 `"200"`、缺码、其他码及无可解释响应返回 unconfirmed；不会把其他码猜成确定失败。同步异常和 Promise 拒绝沿原请求链原样传播，不 catch 改判、不重试。
- 数组按原顺序逐项映射，重复标识不去重。`{ id: 'R1' } → { id: 'R1' }`，`null → {}`，`{ name: '说明' } → { label: '说明' }`。不剔除缺项行、不回退读取旧 label、不增加 detail 请求；非字符串字段不强制转为字符串。
- 数值成功码下，实际空数组映射为 `options: []`，表示当前页无记录；没有可读取数组时省略 options，表示暂无列表数据，不能推断业务无匹配，也不能改判失败。可用 nextPage 独立转交，不触发后续请求。
- 展示层可按 `option.label ?? ''` 显示空名称；读取视图允许没有 id。后续保存必须取得用户实际选中的那条 option 的真实、非空 id，并沿用所属提交内容的确认依据；缺 id 或空 id 的行不能生成保存参数。不能用 label、行号、随机值或占位文本补 id；渲染用的行 key 也不是业务身份。重复 id 保持事实，不在适配器中选择其中一行或重写标识。无名称但有真实 id 的行不因展示缺项被判为接口失败。

已执行验证：通过 `node --input-type=module` 使用 Node.js 内置 node:test 与 strict assert，直接导入本输出目录的真实 readReasons 实现，共 10 项测试通过，0 失败。替换的是 api.list 的网络边界，不替换 readReasons 或内部映射函数；额外依赖设置为访问即抛错的 getter，验证其不会被读取。测试覆盖导出、缺参与页码校验后零调用、指定页仅调用一次、name 映射、旧 label 不回退、null 与缺字段和重复标识保序、空数组与不可读取 data 的区别、严格成功码、nextPage 不引发翻页、稀疏数组位置保留，以及异步拒绝和同步异常原样传播且不重试。未安装依赖、调用网络或设备，未改真实业务工程。

拟在真实工程接入后执行：目标单元的真实 readReasons/既有适配测试、相关 TypeScript 和工程静态规则检查，按静态引用确认公共入口和直接消费者仍使用 label、按需翻页，并核对既有选择到保存交接中真实 id 的校验。若该交接已有覆盖且逻辑未改，沿用对应有效验证；发现受本次映射影响或缺少必要输入检查时，再限定范围补对应场景用例，不在适配器中添加保存或确认行为。后端实际 DTO 和码语义可在必要联调中核实；本次 Node 测试不证明真实服务、真实消费者或接线已通过。

本批业务语义和公共契约不变，不因一个响应字段改名默认扩大为全营销领域测试、所有页面改造、AI 模型任务评测、H5/原生设备或真机验证，也不新增缓存、草稿和确认的验证工程。只有实际发现公共语义、调用顺序、结果范围、共享状态或跨入口关系受影响，才扩大至相关消费者和组合。系统合并、发布仍执行目标工程既定完整 CI，本次定向测试不替代这些门禁；本次尚未执行类型检查、真实工程测试、联调或完整 CI。
