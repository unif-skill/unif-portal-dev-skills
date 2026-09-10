# 设备与领域适配的定向修改

依据所提供的 `portal-development`、`architecture-design` 及其规范快照，本批保持 `pickImage`、`readReasons` 的公开名称和原有业务语义。A 是能力内部等价整理，B 是原始响应字段变化的适配；已有契约足以限定本批，不需要重新设计完整模块。

## A. 图片选择能力

### 最小文件组织与代码

保留已使用的公开文件路径 `capabilities/imagePicker/pickImage.ts`，新增有实际内容的两个角色文件即可：

```text
capabilities/imagePicker/
├── pickImage.ts       # 原公开操作，保留调用和结果语义
├── types.ts           # 本能力的输入与 SDK 结构
└── constants.ts       # 固定默认数量
```

不为这次整理增加总入口、状态文件或平台版本。若工程原来已有该单元的小型 `index.ts`，继续保留其原有公开导出。内部类型、常量不因搬文件就全部成为公共 API。

```ts
// capabilities/imagePicker/types.ts
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

以上 SDK 结构直接依据题设，实际工程若 SDK 已公开这些类型，应引用其公开类型，不再维护重复声明。本题没有已采用的 Schema 或生成器，不引入一套。

```ts
// capabilities/imagePicker/constants.ts
export const DEFAULT_LIMIT = 1;
```

```ts
// capabilities/imagePicker/pickImage.ts
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

`DEFAULT_LIMIT` 是与调用和实例无关的固定默认值，放在所属 `constants.ts`。`controller`、`chosen`、`limit`、`files` 都属于本次调用，即使使用 `const` 也必须留在函数内：它们分别承载取消信号、选中项、输入计算值和异步返回值。SDK 实例属于应用组装及其实际生命周期；由 bootstrap 按现有方式提供给调用链，最终继续执行 `pickImage(input, sdk)`。能力不导入 `app/bootstrap`，也不从全局 `config/sdk.ts` 读取实例。

题设函数只在内部创建控制器并把信号交给 SDK，没有向调用方暴露取消句柄。本批既不新增这种接口，也不增加自动 `abort()`、取消吞错、重试或结果包装。SDK 拒绝继续向外传播；SDK 正常返回空数组仍得到空数组。原生宿主和 Web 支持范围沿用现有实现及接线。正式 Web 代码必须执行已有支持的行为，或按既有契约表达不支持；不能直接伪造“选择成功”，也不把测试替身放进正式平台实现。

### 定向验证

真实被测单元是整理后的 `pickImage`，替换外部 `PickerSdk`，而不是把 `pickImage` 本身 mock 掉。除类型检查、导入方向、公开路径及引用检查外，优先验证：

- 省略 `limit` 时传入 `1`；显式数量原样传递。`0` 也应仍按原函数传入 `0`，不能把 `??` 改成 `||` 或顺带新增限额校验。
- 每次只调用 SDK 一次，并传入本次调用的 `AbortSignal`。并行调用具有不同的 signal，各自选中项独立；成功或拒绝不污染下一次调用。
- 例如 SDK 返回 `['u2', 'u1', 'u2']`，结果为 `['u2', 'u1']`，保持去重和首次插入顺序；空数组仍为空数组。
- SDK 按既有方式抛出取消或其他错误时，外层保持同样的拒绝语义，不变成成功、空结果或重试。题设未给出取消错误分类，不为其补造规则。
- 核对照片选择场景、头像选择和 H5 图片选择桥三个实际消费者的公开路径与调用接线。对受此次引用整理影响的调用路径做窄范围回归，验证同样的输入、结果及取消传播。H5 关系不能只靠静态 import 推定已覆盖。
- 核对 bootstrap 仍向实际调用链提供原 SDK 实例；若仅移动本单元的类型和常量，无须修改宿主初始化，更不能把“未修改宿主”报告为“已做真机验证”。

默认数量虽然本次只移动位置，其对外行为仍须断言为 `1`。将来若改默认值，要验证照片选择、头像选择和 H5 在未指定数量时的实际行为；TypeScript 通过不能证明默认值兼容。

## B. 原因选项读取适配

### 最小组织与职责

沿用 `domains/marketing/reasons` 及公开入口 `readReasons`。原始 DTO、对应接口成功码和字段转换留在该功能所属的适配边界，页面只消费既有功能结果。若已有适配文件，直接修改它；下面是需要明确原始协议子单元时的最小布局示意，不要求把已有合规文件重新搬成另一套目录：

```text
domains/marketing/reasons/
├── readReasons.ts             # 已有公开读取操作
├── types.ts                   # 既有功能结果、可选显示字段与依赖类型
└── adapter/
    ├── readReasonsResponse.ts # 原始响应解释与字段映射
    ├── types.ts               # 本接口原始 DTO、边界读取结构
    └── constants.ts           # 本接口已确认成功码
```

原有小型公共出口只继续导出消费者实际使用的入口和类型，不导出原始信封、码表或内部辅助。公共 HTTP、认证与取消处理继续使用原链路。适配器不把 DTO 放进全局 `types/`，也不把码表放进全局 `config/`；其他接口的码表不因本批修改一并收集。

`readReasons` 只读取并给出原因选项。完成场景负责原因选择、必要输入检查、调用现有保存操作及后续完成步骤。读取过程中不保存、不默认选择第一条，不新增写请求、重试或自动完成。

### 关键类型和结果处理

题设没有给出现有功能结果的完整字段名、状态值和构造函数，下面以 `label` 表示原有可选显示字段，以 `id` 表示真实原因标识。若工程实际采用其他已公开名称，保留原名称；此示意不新建一套公共结果协议。

```ts
// adapter/types.ts：原始 DTO 描述接口应提供的字段。
export interface ReasonDto {
  id: string;
  name: string;
}

export interface ReasonsResponseDto {
  code: number;
  data: ReasonDto[];
}

// 用于读取实际边界数据，不假定服务端一定满足 DTO。
export interface ReasonsResponseView {
  code?: unknown;
  data?: unknown;
}

export interface ReasonView {
  id?: unknown;
  name?: unknown;
}
```

```ts
// reasons/types.ts：在既有公共契约上表达可能缺失的字段。
export interface ReasonOption {
  id?: string;
  label?: string;
}
```

原始 DTO 和功能结果分别描述外部协议与功能语义，二者不合成一个类型。实际读取不能用全对象必填校验把缺值行或 `null` 拒绝掉。

```ts
// adapter/constants.ts
export const SUCCESS_CODE = 200;
```

```ts
// adapter/readReasonsResponse.ts：内部映射核心。
import type { ReasonOption } from '../types';
import type { ReasonView } from './types';

function toReasonOption(value: unknown): ReasonOption {
  const row: ReasonView =
    value !== null && typeof value === 'object' && !Array.isArray(value)
      ? value
      : {};

  return {
    id: typeof row.id === 'string' ? row.id : undefined,
    label: typeof row.name === 'string' ? row.name : undefined,
  };
}

function readOptions(data: unknown): ReasonOption[] | undefined {
  return Array.isArray(data) ? data.map(toReasonOption) : undefined;
}
```

在原有 `readReasons` 适配器中，将 HTTP 返回体先作为不可信边界数据读取，再按如下流程接入原有结果构造与诊断代码：

```text
取得原始 code 和 data
  code === SUCCESS_CODE（严格数值比较）
    → 沿用既有“读取成功”结果，选项为 readOptions(data)
  已有接口契约明确的失败码或其他状态码
    → 沿用相应语义映射
  code 缺失、未知，或 code 为字符串 '200'
    → 沿用既有缺码／未知码的未确认或接入错误处理，不判成功
```

不使用 `Number(code)`、宽松相等或数据非空判断成功。本题只确认数值 `200`，不能自行宣布某个其他码为确定业务失败。原始码及已有请求关联保留在适配层的结果解释和诊断中，不让场景再次比较后端码。

成功码下的结果应具有以下行为：

| 实际数据 | 功能数据与显示 | 后续操作约束 |
|---|---|---|
| `[{id:'R1',name:'原因一'}]` | 一个选项，显示“原因一” | 用户实际选择该项后才可使用 `R1` |
| `[{id:'R1'}]` | 保留该行，显示字段为空，真实 `id` 保留 | 不自动选中；用户实际选择后是否可继续按现有场景约束判断，缺显示名称本身不补造新禁用条件 |
| `[null]` | 保留一个空显示条目，不能过滤、拒绝整页或增加异常计数 | 无真实标识，不能把空值、序号或临时渲染 key 当作保存标识 |
| `[{id:'R1'},null,{id:'R2',name:'原因二'}]` | 保留三个条目及原顺序 | 选择状态跟随真实用户操作，不因缺名改选其他行 |
| `[]` | 成功且本页无记录 | 没有可供选择的实际项 |
| 缺失或不可读取的列表数据 | 成功；结果用现有契约的可选数据表达，显示“暂无列表数据” | 不能推断业务“无匹配”，也不能制造选项 |

显示层可使用 `option.label ?? ''`，但不能把显示回退值复制成 `id`。场景保留“尚未选择”和“用户已选择”的区别，保存前从用户实际选择的条目取得真实、符合已有保存契约的标识。没有选择或没有可用标识时停在选择步骤，按原交互处理，不发保存和最终完成请求。不得用 `options[0]`、行号或“默认原因”补齐身份。

### 类型检查之外的定向验证

真实被测单元是现有 `readReasons` 及其实际适配器，外部 HTTP 依赖使用替身；完成场景测试替换真实业务写入边界。重点断言：

- 数值 `200` 才进入成功分支；`'200'`、缺码和未知码，即使带有效数组，也不成为成功。已有明确失败码按原码表处理。
- `name` 映射到原有显示字段，输出不泄漏原始 DTO 差异。对比旧功能语义与新响应适配后的结果，消费者无需自行解析 `name`。
- `200` 下缺少 `name`、缺少 `id`、`null` 行，以及缺少／不可读取的列表数据，不改判接口失败。列表条目数量和顺序保持不变，不过滤、不补造身份、不增加异常计数。
- 区分真实空数组与没有可读取列表；核对用户看到的空显示、“本页无记录”或“暂无列表数据”所表达的实际含义。
- `readReasons` 完成时没有保存或最终完成副作用；读取失败、未知码、取消同样不能触发写入。保留原传输和取消传播语义。
- 唯一消费者是完成场景的原因选择交互：加载结果不会默认选中第一项；用户选择真实 `R1` 后，场景保存的仍是 `R1`；无选择或选中缺失标识的条目时不发写请求。保存和最终完成仍由原场景按现有顺序协调，不把读取成功当作最终完成成功。

本批优先覆盖原始协议映射测试、`readReasons` 的定向测试和这一个实际场景的选择交接用例。只改 `name` 适配，不要求修改所有页面或重跑所有营销领域测试；系统合并与发布仍按目标工程既有 required CI 执行。

## 何时扩大影响范围

- A 目前已存在 H5 图片选择桥消费者，因此本批已要核对其接线和受影响行为。将来图片选择的默认数量、公共输入输出、取消／错误语义、桥接参数或回包协议变化时，扩大验证到实际受影响的照片、头像和 H5 消费者及跨版本契约。
- 原生 SDK、权限、初始化、宿主注册、平台文件或资源生命周期改变时，增加相关平台构建、宿主接线与真机验证；Web 支持或模块解析发生变化时验证实际 Web 宿主和预览接入。内部文件移动本身不证明需要更改原生配置。
- B 当前无已知 H5 消费者。仅后端字段等价改名不扩大到 H5、宿主或其他设备能力。未来 `readReasons` 公共结果、选择／保存语义、确认责任、共享状态或消费者发生变化时，沿实际生产方、消费者与组合链路扩大验证；新增 H5 消费者后才纳入其协议链路。
- 公共 HTTP、认证、取消机制或共享能力契约真的改变时，覆盖相应共同消费者。若发现当前依赖识别遗漏，则扩大到相关组合或领域并补齐关系，不能以静态检查通过宣称所有影响已覆盖。

本答案为书面组织与代码方案，只读取了题设和指定的两套技能资料。未安装依赖、未修改合成工程实现、未运行类型检查或测试、未访问 SDK 或业务系统，亦未完成真机、Web 宿主或远端 CI 验证。文中验证项是本批应执行的范围，不是已取得的通过证据。
