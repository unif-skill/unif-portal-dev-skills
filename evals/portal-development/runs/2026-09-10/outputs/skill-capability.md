# 设备与领域适配的定向修改方案

依据本次 `portal-development/SKILL.md` 及其包内开发规则第 2—5 节、工程组织第 3—6 节、平台架构第 6 节。以下为书面方案；没有读取真实工程、访问 SDK 或业务系统，没有安装依赖、修改工程源码或执行测试。题设未给出的现有公共字段、返回状态名和 HTTP 接线不能据此补造为正式契约。

## A. 保持 pickImage 语义的文件整理

保留 `capabilities/imagePicker/pickImage.ts` 这个明确公开文件及 `pickImage` 名称、双参数签名。最小组织为：

```text
src/
  capabilities/imagePicker/
    pickImage.ts                 # 原公开入口，独立设备操作
    types.ts                     # 已有输入与 SDK 依赖接口
    constants.ts                 # 固定默认数量
  app/bootstrap/                 # 沿用已有 SDK 初始化和向消费者接线
__tests__/capabilities/imagePicker/
  pickImage.test.ts              # 定向行为测试
```

不需要额外 index.ts、state.ts、全局 SDK 配置、宿主文件或空平台文件。若真实工程已有小型 index.ts，则保持它当前所需出口；跨单元继续使用已确认的公开入口。应用组装所需依赖类型可从明确的 `types.ts` 公开文件取得，不导出内部运行状态。

`types.ts`：

```ts
export interface PickInput {
  limit?: number;
}

export interface PickerSdkInput {
  limit: number;
  signal: AbortSignal;
}

export interface PickerSdk {
  pick(input: PickerSdkInput): Promise<string[]>;
}
```

`constants.ts`：

```ts
export const DEFAULT_LIMIT = 1;
```

`pickImage.ts`：

```ts
import { DEFAULT_LIMIT } from './constants';
import type { PickInput, PickerSdk } from './types';

export async function pickImage(input: PickInput, sdk: PickerSdk) {
  const controller = new AbortController();
  const chosen = new Map<string, number>();
  const limit = input.limit ?? DEFAULT_LIMIT;
  const files = await sdk.pick({ limit, signal: controller.signal });
  files.forEach((uri, index) => chosen.set(uri, index));
  return Array.from(chosen.keys());
}
```

只有 `DEFAULT_LIMIT` 是固定默认值。controller、chosen、limit、files 都保留调用作用域；SDK 实例是 bootstrap 提供的运行期依赖，由参数传入。能力不 import `app/bootstrap`，也不从 `config/sdk.ts` 取全局实例。

真实接线应继续是 bootstrap 创建或取得 SDK，照片选择场景、头像选择和 H5 图片选择桥经既有接线路径调用 `pickImage(input, sdk)`。本题已经提供该注入形式，无需引入注册中心、容器或新工厂。接口抽出后核对这三个消费者及 bootstrap 的类型导入，不能只检查照片选择。

这段代码保留原行为：`??` 只对空缺输入应用默认值，不新增正数校验、上限截断或用 `||` 改写 0；URI 去重保持 Map 的首次插入顺序；SDK 的空数组仍返回空数组，拒绝仍原样传播。原代码没有对外取消参数、catch 转换或自动 abort，本次也不新增取消 API、取消结果或 finally 中的 abort。独立 controller 仍每次创建并传入此次 SDK 调用。

Web 支持范围保持现状。题设没有提供其现有支持契约，不能写一个“选择成功”替身，也不能据此擅自改成新的失败码。沿用既有实际 Web 实现或既有明确不支持的适配，确认它在当前导入路径下仍能解析；测试用 SDK 替身仅留测试环境。

### A 的定向验证

- 静态：类型检查和当前工程已有导入检查；确认三个消费者及 bootstrap 都能引用原公开入口，能力不反向依赖 app、不产生循环；AST 或审查区分固定值与调用局部变量。
- 行为：默认值严格为 1、显式 limit 透传（包括 0）、空数组、重复 URI 去重及首次出现顺序；SDK 拒绝对象原样传播；每次调用仅发起一次 pick。
- 隔离：两次并发调用捕获的 signal 不同，各调用结果互不污染；SDK 初始收到未中止 signal。按原有 SDK 取消行为的替身返回或拒绝验证传播，不虚构取消约定。
- 消费者：照片场景、头像场景、H5 图片选择桥各自的输入转换和既有结果/取消解释，特别是桥请求到能力到回包的实际接线。bootstrap 用替身证明传入的是组装提供的实例。H5 是已经存在的消费者，本次即需定向覆盖，不能留到将来。
- 平台：只核对现有 Web 支持路径和必要的相关编译/适配测试；原生宿主、SDK、权限及支持范围未变，不因拆文件默认要求全套设备测试或其他能力测试。真实原生构建与设备行为本答未验证。

后续若默认数量改值，即使类型检查通过，也应重验三个实际消费者依赖的数量语义；若 H5 请求/回包、共享公开结果或取消协议改变，应扩大桥协议契约验证；若 SDK、宿主初始化、资源释放、平台实现或支持范围改变，再补相关平台构建、真机、Web 宿主和多实例生命周期验证。只有出现实际共享契约或接线影响，才扩大到其他能力。

## B. readReasons 内的原始字段适配

保留现有 `domains/marketing/reasons` 单元、`readReasons` 名称及其公开输入输出语义。原始 `name` 在单元内部映射到当前功能的可选显示字段，完成场景继续消费相同功能结果。保存原因及最终完成仍由完成场景协调。

若现有适配尚未独立，最小组织可为：

```text
src/domains/marketing/reasons/
  readReasons.ts                # 原公共查询入口；沿用当前传输接线
  types.ts                      # 当前功能公开类型，不改公开名称
  adapter/
    readReasonsResponse.ts      # 本接口的成功码解释和字段转换
    types.ts                    # 本接口原始 DTO、内部读取类型
    constants.ts                # 本接口确定的成功码
__tests__/domains/marketing/reasons/
  readReasons.test.ts
  readReasonsResponse.test.ts
__tests__/domains/marketing/<现有完成场景>/
  <现有原因选择行为>.test.tsx
```

`adapter/` 是这个功能内确有独立原始契约的子单元；若工程已有适配文件则原位修改，不新增第二套结构。最终文件路径按真实既有文件落实；上面场景测试路径是归属示意，不假称题设给出了其名称。HTTP、认证、取消及其全局实现不改；不新增全局 DTO/码表仓库，不让页面各自读 `code`、`name`，不在查询里调用保存。

下面给出可独立审查的内部转换代码。题设没有公开结果类型的确切名字和包装形态，因此 `ReasonReadView`、`MappedReasonsSuccess` 仅表示适配器内部结构，不能新增导出到公共入口。示例以 `label` 指代当前可选显示字段；真实工程须使用其既有字段名及既有成功包装。原始契约与功能契约表达不同边界，各自单一维护。

`adapter/constants.ts`：

```ts
export const READ_REASONS_SUCCESS_CODE = 200;
```

`adapter/types.ts`：

```ts
// 原始协议应提供的结构，不为容忍实际缺字段而抹去原始契约。
export interface ReasonDto {
  id: string;
  name: string;
}

// 原始应有结构的描述；网络边界仍以 unknown 接收和检查。
export interface ReadReasonsSuccessDto {
  code: 200;
  data: ReasonDto[];
}

// 容忍真实读取缺失的内部视图，不作业务写入身份的保证。
export interface ReasonReadView {
  id?: string;
  label?: string;
}

export interface MappedReasonsSuccess {
  reasons?: ReasonReadView[];
}

export interface UnknownFields {
  [key: string]: unknown;
}
```

`adapter/readReasonsResponse.ts`：

```ts
import { READ_REASONS_SUCCESS_CODE } from './constants';
import type {
  MappedReasonsSuccess,
  ReasonReadView,
  UnknownFields,
} from './types';

function isObject(value: unknown): value is UnknownFields {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function mapReason(value: unknown): ReasonReadView {
  if (!isObject(value)) return {};
  return {
    id: typeof value.id === 'string' ? value.id : undefined,
    label: typeof value.name === 'string' ? value.name : undefined,
  };
}

// undefined 表示未命中本接口已确认的成功码，交回现有非成功解释路径。
// { reasons: undefined } 则是已确认成功但没有可读取列表，二者不同。
export function readReasonsResponse(
  value: unknown,
): MappedReasonsSuccess | undefined {
  if (!isObject(value) || value.code !== READ_REASONS_SUCCESS_CODE) {
    return undefined;
  }
  return {
    reasons: Array.isArray(value.data)
      ? value.data.map(mapReason)
      : undefined,
  };
}
```

`readReasons.ts` 保留当前 HTTP 调用、认证和取消方式；在取得原始响应后调用此内部映射。命中成功时将 `reasons` 放入**现有功能成功结果**；未命中时沿用该接口既有业务拒绝、其他状态或未确认的解释路径，并保留原码及当前请求关联。只知道 200 成功，不能自行规定“全部其他码都是确定失败”，也不能把字符串 `'200'` 转成数字。不存在明确码表的分支按现有未确认机制处理，不重新调用、不自动保存。本题未给出现有结果构造函数或 HTTP API，所以不伪造可直接替换的完整 `readReasons` 函数签名。

对以下响应，转换结果可具体审查：

```ts
// 输入
{
  code: 200,
  data: [
    { id: 'R0', name: '已有名称' },
    { id: 'R1' },
    null,
  ],
}

// 现有成功结果中的列表内容（label 指代既有显示字段）
[
  { id: 'R0', label: '已有名称' },
  { id: 'R1', label: undefined },
  {},
]
```

三个条目及顺序保留，不过滤 null、不把缺名称记录丢掉，不把整个成功响应改判失败。交互对缺少显示字段使用空显示；不补造原因名称或标识，不增加“成功但数据异常”状态。真实 `data: []` 表示本页无记录；没有可读列表表示暂无列表数据，不直接推断业务无匹配，且仍属于码已确认的成功结果。

完成场景的选择状态保持未选择，直到用户确实做出选择。缺少名称不触发默认选第一项。保存前在场景既有输入校验处检查所选记录的真实原因标识，不能用数组索引、空串、占位值或别项 id 代替。`{id:'R1'}` 的真实 id 不因名称缺失丢失；null 行不具备可用于保存的 id。若 UI 使用索引作为缺 id 行的渲染 key，该 key 也绝不能进入保存参数。保存与最终完成继续按场景当前步骤及确认规则执行，读取选项本身没有写入副作用。

### B 的定向验证

- 适配契约：数值 `200` 成功；字符串 `'200'`、缺 code 和未知 code 即使有非空 data 也不成功；已知业务失败或其他状态按现有该接口码表，不改变公共 HTTP 的码值解释。
- 字段兼容：`name` 正确映射到原功能可选显示字段；功能消费者不用读取原始 `name` 或业务码；本题没有双协议支持要求，不额外引入 `name ?? label` 猜测回退。
- 列表行为：完整行、`{id:'R1'}`、null 混合列表输出长度与顺序不变；缺名称为空显示；真实 id 原样保留；`200 + []`、`200 + null`、缺 data 分别覆盖，均不因 data 缺项改判接口失败，且空数组与不可读取列表可区分。
- 完成场景：加载后保持未选择；不因缺名称默认选第一项；用户所选真实 id 进入原保存入口；缺 id 行不能产生保存请求；读取、渲染、选择动作均不暗中调用保存或最终完成。可用保存函数 spy 断言读取后调用次数为 0。
- 现有取消/异常：传输拒绝、取消继续沿原路径传播或映射，无新请求、新重试或成功替身。
- 类型和导入：原 `readReasons` 公开消费者仍能编译；DTO、成功码只在该功能适配器解释；完成场景导入公开功能类型，不穿透 adapter。

B 当前唯一消费者为完成场景的原因选择交互，因此本批聚焦该适配器、查询入口及该场景交互测试，不默认扩展到 H5、原生宿主、其他设备能力或全营销领域。将来若 H5 开始消费该功能、公开结果或桥协议发生变化、共享 HTTP/认证/取消协议被修改，或完成场景新增实际宿主/能力依赖，再沿真实调用链扩大对应契约和接线测试。后端字段名变化本身不构成扩大上述范围的理由。

## 交付证据边界

已执行的工作只有读取题设和指定技能资料、形成本文；没有运行 TypeScript、ESLint、Jest、构建或设备检查。以上是落地时应执行的定向验证范围，不能宣称已经通过。实际工程若具备角色文件、导入方向、循环依赖等静态门禁，应使用现有配置运行；技能中的要求不等于工程已经强制实现这些门禁。
