# 两项定向修改

依据为给定的 PORTAL_DEVELOPMENT.md 第 1—5 节、PORTAL_STRUCTURE.md 第 3—6 节和 ARCHITECTURE.md 第 6 节。本答案为书面实施方案；未安装依赖、访问 SDK 或业务系统，也未实际运行验证。保留 `pickImage`、`readReasons` 公开名称。B 未给出现有完整签名和结果状态字段，以下给出可直接对应到既有结构的核心适配代码与接线片段，不声称已确定其未提供的接口、错误码或请求参数。

## A. imagePicker 内部整理

最小文件组织（src 为题设能力路径的源码根）：

```text
src/capabilities/imagePicker/
  pickImage.ts       # 保留已有公开文件与函数
  types.ts           # 输入与可替换 SDK 契约
  constants.ts       # 固定默认值
__tests__/capabilities/imagePicker/
  pickImage.test.ts
```

已有公开 `pickImage.ts` 足以作为入口，不为此强制增设 index.ts；若工程原有小型 index.ts，则继续由它具名导出实际公共接口。SDK 的调用输入对象是手写结构，亦放入同单元 types.ts：

```ts
// capabilities/imagePicker/types.ts
export interface PickInput {
  limit?: number;
}

export interface PickerPickInput {
  limit: number;
  signal: AbortSignal;
}

export interface PickerSdk {
  pick(input: PickerPickInput): Promise<string[]>;
}
```

```ts
// capabilities/imagePicker/constants.ts
export const DEFAULT_LIMIT = 1;
```

```ts
// capabilities/imagePicker/pickImage.ts
import { DEFAULT_LIMIT } from './constants';
import type { PickInput, PickerSdk } from './types';

export type { PickInput, PickerSdk } from './types';

export async function pickImage(input: PickInput, sdk: PickerSdk) {
  const controller = new AbortController();
  const chosen = new Map<string, number>();
  const limit = input.limit ?? DEFAULT_LIMIT;
  const files = await sdk.pick({ limit, signal: controller.signal });
  files.forEach((uri, index) => chosen.set(uri, index));
  return Array.from(chosen.keys());
}
```

`controller`、`chosen`、`limit`、`files` 均留在调用内。SDK 是 bootstrap 已提供的运行期依赖，继续以参数传入；不放入 constants.ts 或全局 config，也不让能力反向 import app/bootstrap。上层已有组装处将同一真实实现传入三个消费者，示意如下，不新增注册中心或全应用依赖对象：

```ts
// 在已有 bootstrap 组装作用域中，pickerSdk 是现有实例：
const selectImage = (input: PickInput) => pickImage(input, pickerSdk);
// 将 selectImage 传给照片选择场景、头像选择入口、H5 图片选择桥的已有接线点。
```

这里的闭包留在实际组装作用域；能力不读取它。原生宿主及 SDK 初始化、释放责任维持现有接线。操作控制器只属于本次调用，当前接口并没有向调用者提供取消方法。本次不会加 abort 参数、把取消改为空数组、在 finally 中新加 abort，或改变 SDK rejection 的传递方式。原实现如何由 SDK 表达取消，整理后即如何表达；不能根据函数内部创建 controller 推断已有外部取消能力。

平台文件仅在已有平台差异要求下维护。本批既不扩大 Web 支持，也不新增“成功”的 Web 替身；保留现有实际实现或既有明确不支持结果。因题设未提供现有 Web 错误契约，不能擅自发明新的错误码。SDK 测试替身只存在测试环境。

验证范围：

- 能力行为：遗漏 limit 时 SDK 收到 1；显式 limit 原样传递，尤其原有 `??` 语义下 0 仍为 0；重复 URI 去重且按首次出现顺序返回；空数组返回空数组。
- 资源隔离：两次并发调用分别得到不同 AbortSignal，互不共享 chosen；一次调用的数据、失败或取消不会污染另一次结果。每次只调用 SDK 一次。
- 取消与失败：用替代 SDK 重放原有取消返回或 rejection、普通 rejection，断言原样传递，无新增重试、自动提交或错误吞没。题设未定义的 SDK 取消细节不能宣称已验证。
- 接线与消费者：核对照片选择、头像选择、H5 图片选择桥三个实际消费者的导入与依赖传入，运行各自受影响的调用/结果映射测试；H5 关系不能仅靠静态 import 搜索排除。bootstrap 的依赖传递做定向接线验证。
- 类型、固定值与导入方向检查覆盖这些改动。DEFAULT_LIMIT 未改值，仍需默认 1 的行为断言，不能以编译通过代替。原生和 Web 支持未变，不要求凭此重跑全部设备能力或原生构建；本答案也不宣称通过真机、Web 宿主或实际 H5 联调。

## B. reasons 的字段适配

单元职责仍是只读原因查询，唯一消费链是完成场景的原因选择交互。原始 DTO、所属接口的成功码和映射留在该功能适配器内部；不把原始协议搬到全局 types/config，不让每个页面映射，不在 readReasons 内调用保存或完成。

最小组织示意如下。如果现有单元已有同职责适配文件，直接在其中修改，不再平行新增一套目录：

```text
src/domains/marketing/reasons/
  readReasons.ts
  types.ts                     # 既有功能公开结果；可选显示字段语义不变
  index.ts                     # 既有必要公开出口
  adapter/
    types.ts                   # 所属接口 DTO 和宽容读取视图
    constants.ts               # 仅该接口已确认的码
    mapReasons.ts              # 信封读取与 name 到既有 label 的投影
__tests__/domains/marketing/reasons/
  readReasons.test.ts
  mapReasons.test.ts
__tests__/domains/marketing/<既有完成场景>/
  <既有原因选择行为>.test.tsx
```

尖括号表示沿用工程已有场景路径，不是建议新建同名字面目录。功能输出下面以 `ReasonOption.id` 和可选 `label` 表示题设的真实标识与原有显示语义；如实际公开字段不同，保持其已有名称。

```ts
// reasons/types.ts 中既有选项结构
export interface ReasonOption {
  id?: string;
  label?: string;
}
```

内部 DTO 表达接口应提供的结构；读取视图允许实际缺项，避免以整行必填校验剔除 null 或缺字段条目：

```ts
// reasons/adapter/types.ts
export interface ReasonDto {
  id: string;
  name: string;
}

export interface ReasonsResponseDto {
  code: number;
  data: ReasonDto[];
}

export interface ReasonsEnvelopeView {
  code?: unknown;
  data?: unknown;
}

export interface ReasonRowView {
  id?: unknown;
  name?: unknown;
}
```

```ts
// reasons/adapter/constants.ts
export const READ_REASONS_SUCCESS_CODE = 200;
```

```ts
// reasons/adapter/mapReasons.ts
import type { ReasonOption } from '../types';
import type { ReasonRowView, ReasonsEnvelopeView } from './types';

export function readEnvelope(raw: unknown): ReasonsEnvelopeView {
  return raw !== null && typeof raw === 'object'
    ? (raw as ReasonsEnvelopeView)
    : {};
}

export function mapReasons(data: unknown): ReasonOption[] | undefined {
  if (!Array.isArray(data)) return undefined;

  return data.map((value: unknown): ReasonOption => {
    const row: ReasonRowView =
      value !== null && typeof value === 'object'
        ? (value as ReasonRowView)
        : {};
    return {
      id: typeof row.id === 'string' ? row.id : undefined,
      label: typeof row.name === 'string' ? row.name : undefined,
    };
  });
}
```

这两个导出仅供本功能内部协作，不通过 reasons/index.ts 暴露。`name` 是新原始协议字段，映射回现有功能显示字段；没有需求依据增加 `name ?? label` 的双版本兼容。没有 filter、异常计数、生成 ID 或取首条默认选择。`null` 投影为空字段选项，仍保留对应位置；数组中的全部条目及顺序不变。

`readReasons` 继续调用原有请求一次。以下是应替换的结果处理逻辑片段，`requestReasons`、`existingSuccess`、`existingNonSuccess`、`recordResponseCode` 代表原有请求、结果构造和请求诊断位置，不是新增接口或依赖；完整原签名、传输异常及取消处理保持不变：

```ts
const raw = await requestReasons(/* 原有参数、认证与取消接线 */);
const envelope = readEnvelope(raw);
recordResponseCode(envelope.code); // 沿用该请求现有诊断关联，不向页面暴露码表

if (envelope.code === READ_REASONS_SUCCESS_CODE) {
  return existingSuccess(mapReasons(envelope.data));
}
return existingNonSuccess(envelope.code); // 按所属接口已有明确码表解释
```

只有数值 200 进入成功分支。字符串 '200' 不转换为数值，不被认定成功；题设未给出的其他码不擅自列为明确失败，缺码或未知码走既有结果未确认语义。HTTP 成功、data 非空或包含 id 都不能取代业务码。不要为本批修改公共 HTTP 客户端。

成功结果中的数组缺项不改判失败。例如：

```text
原始：{ code: 200, data: [{ id: 'R1' }, null, { id: 'R2', name: '其他原因' }] }
投影：成功，[
  { id: 'R1', label: undefined },
  { id: undefined, label: undefined },
  { id: 'R2', label: '其他原因' }
]
```

交互可用 `option.label ?? ''` 空显示，不把空名称替换成伪造原因。用户尚未选择时，选择状态仍为空；不得由于名称缺失自动选首项。选择状态由完成场景维护。用户真实选择 R1 后，名称缺失不消灭真实 id，保存可使用 R1；选择到没有真实 id 的条目时不得发起需要原因标识的保存。展示行下标即便用于渲染键，也不能变成业务 id。保存与最终完成只由既有场景按实际用户动作、必要输入和既有规则协调，不增加自动确认或读取后写入。

`data: []` 表示当前列表无记录；`data` 不存在或不可读取时，仍为 code 200 对应的成功，只展示暂无列表数据，不推断业务无匹配。示例 `undefined` 表达这种差别，接到现有功能结果的可选列表字段；不新设“成功但回执异常”状态。

验证范围：

- 适配契约：数值 200 成功；字符串 '200'、缺码、未知码、传输异常不得变成成功，既有明确失败码按所属码表验证。保留原始码及请求关联的既有诊断路径。
- 字段投影：name 映射到既有可选显示字段；id 原样保留；上述混合数组长度和顺序完全一致，缺名行及 null 均不丢失，无伪造 id、首项替代或异常计数。空数组与不可读取列表分别断言其展示语义；二者不改变数值 200 的业务成功。
- 只读副作用：readReasons 只调用读取一次，保存和最终完成调用次数均为 0；不增加重试、认证刷新或取消协议变化。
- 唯一消费者的交互：读完保持未选择；缺名不触发选择；用户选择真实 R1 后传递 R1；缺 id 时不保存；切换选择不被旧列表首项覆盖。已有保存与完成的协调路径做受影响的定向回归，验证真实选择和调用参数。
- 类型与导入检查覆盖公开结果、适配私有类型及唯一实际消费者；核心行为由适配和交互测试证明，编译不能证明字符串码不会误判，也不能证明没有自动保存。

B 本批没有 H5、宿主或其他设备能力的消费关系变化，只测适配及完成场景的原因选择链路，不默认重跑整个 marketing 或全部设备测试。测试范围仍需核对真实依赖，题设以外的工程 CI、联调和设备证据均未提供。

## 何时扩大验证范围

- A 后续修改公开默认数量、输入输出、错误或取消语义时，覆盖照片、头像及 H5 桥的实际协议映射与用户行为；即使类型不变，默认数量变化也属于语义变化。
- A 修改 SDK 版本、原生权限或配置、初始化/释放、宿主注册、平台实现或 Web 支持时，增加对应宿主接线、多实例与卸载验证，并按影响补平台构建、真机、Web 预览和 H5 联调。
- B 后续改变功能结果、选择要求、保存/完成顺序，或新增 H5/其他场景消费者时，扩大到对应契约与组合。改公共 HTTP、认证或取消时再依据全部真实受影响调用扩大，不能因为本次 raw name 改名就波及所有页面。
- 任何一项若触及被其他能力共享的实际依赖，补那些能力的相关测试；只有目录相邻不构成扩测理由。发现静态测试选择遗漏 H5、宿主或跨仓契约关系时，按真实链路补齐。系统合并与发布仍执行目标工程既定 CI。
