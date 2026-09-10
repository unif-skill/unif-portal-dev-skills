两项改动分别限定在 `capabilities/imagePicker` 和 `domains/marketing/reasons`。保留 `pickImage`、`readReasons` 及已有公开调用方式；文件整理不改变取消、副作用或平台支持范围。

本方案使用 `portal-development` 的文件角色、依赖方向和定向验证规则，并用 `architecture-design` 的交接契约核对业务成功、缺值展示与后续操作输入。以下路径均指合成工程中的相对路径，不代表已修改真实工程。

**A. 设备能力：三个实际需要的文件。**

```text
capabilities/imagePicker/
  pickImage.ts      # 保留现有公开入口与实现名称
  types.ts          # 输入与 SDK 接口
  constants.ts      # 固定默认数量
```

沿用已有公开出口；原来没有 `index.ts` 时，不为本批新增一层出口。若已经有小型 `index.ts`，保留已有具名导出，不顺便公开内部常量和类型。照片选择场景、头像选择、H5 图片选择桥均继续调用原公开入口。

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

这里的 `export` 用于单元内部跨文件引用，并不要求加入公共 barrel。若工程已经公开导出默认数量，则保留原来的公开出口。

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

只有 `DEFAULT_LIMIT` 是不依赖调用的固定值。`controller`、`chosen`、计算后的 `limit`、返回的 `files` 均留在函数内；`sdk` 继续由调用参数取得。把控制器或 Map 移到模块级会共享不同调用的资源和状态；把 SDK 移到全局配置并从能力反向读取 bootstrap，会破坏依赖方向。

应用 bootstrap 继续持有并提供实际 SDK 实例，沿已有接线传入上述参数，不新增全局容器、注册中心或单例。无需仅为移动类型和常量修改 SDK 初始化。

保持原算法的精确行为：未提供数量时传 `1`；显式数量原样透传，`0` 也不被 `||` 替换；同 URI 去重且保留首次出现的顺序；空数组仍返回空数组；SDK 拒绝沿原路径抛出。原代码虽然创建了控制器，但没有暴露外部取消入口，也没有主动调用 `abort()`，本批不能顺手增加这两种行为或把 SDK 取消改成成功空结果。

不增加“选择成功”的 Web 替身。保留现有 Web 实现或现有明确表达不支持的适配，以及现有 `.native`、`.web` 文件解析关系；正式平台实现不能用测试假实现冒充设备完成。材料未给出 Web 的既有不支持结果结构，因此本批不另造错误码或结果对象。

**B. 原因读取：字段适配留在现有领域单元。**

```text
domains/marketing/reasons/
  readReasons.ts    # 原请求调用与私有响应适配
  types.ts          # 已有功能类型、原始 DTO、必要内部读取类型
  constants.ts      # 本接口已确认的成功码
```

优先合并进已有角色文件。`readReasons.ts` 可以容纳这些短小的私有适配函数，不为本批另建服务类或转换框架。公共出口继续只暴露原功能契约；原始 DTO、业务码和转换函数不进入全局 `types/`、`config/`，也不交给每个页面重复解释。

下面给出完整的私有适配核心。`ReasonOption` 是代码示例中的说明性名称；接入工程时引用已有功能结果类型并保留其公开名称与显示字段。示例以原来的显示字段 `label` 表达相同功能语义，将新协议字段 `name` 映射到它。私有 `kind` 分支也不是新增公共结果协议。

`types.ts` 中的相关结构：

```ts
// 原始 DTO 描述接口约定应提供的字段，不将缺值情况改写成规范要求。
export interface ReasonDto {
  id: string;
  name: string;
}

export interface ReasonsResponseDto {
  code: number;
  data: ReasonDto[];
}

// 读取视图容纳实际响应的缺项，展示值不能替代业务身份。
export interface ReasonOption {
  id?: string;
  label?: string;
}

export interface AdaptedReasonsSuccess {
  kind: 'success';
  code: 200;
  options?: ReasonOption[];
}

export interface AdaptedReasonsUnconfirmed {
  kind: 'unconfirmed';
  code: unknown;
}

export type AdaptedReasonsResult =
  | AdaptedReasonsSuccess
  | AdaptedReasonsUnconfirmed;
```

`constants.ts`：

```ts
export const READ_REASONS_SUCCESS_CODE = 200;
```

`readReasons.ts` 中新增或替换对应的私有转换部分：

```ts
import { READ_REASONS_SUCCESS_CODE } from './constants';
import type { AdaptedReasonsResult, ReasonOption } from './types';

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return typeof value === 'object' &&
    value !== null &&
    !Array.isArray(value)
    ? value as Record<string, unknown>
    : undefined;
}

function readReasonOptions(data: unknown): ReasonOption[] | undefined {
  if (!Array.isArray(data)) return undefined;

  return Array.from(data, item => {
    const row = asRecord(item);
    return {
      id: typeof row?.id === 'string' ? row.id : undefined,
      label: typeof row?.name === 'string' ? row.name : undefined,
    };
  });
}

function adaptReasonsResponse(raw: unknown): AdaptedReasonsResult {
  const envelope = asRecord(raw);
  const code = envelope?.code;

  if (code === READ_REASONS_SUCCESS_CODE) {
    return {
      kind: 'success',
      code,
      options: readReasonOptions(envelope?.data),
    };
  }

  // 本题仅确认数值 200。其他码不能凭非空 data 或类型转换推断成功。
  return { kind: 'unconfirmed', code };
}
```

在已有 `readReasons` 内，用 `adaptReasonsResponse` 处理原请求得到的响应，再封装为已有功能公共结果。保留原请求关联和原始码用于该请求的诊断；消费者只接收语义化结果。材料没有给出 `readReasons` 的完整签名、现有结果分支及请求 API，因此这里不虚构这些部分，也不把上述私有结构直接替换成新的公开返回类型。若工程已有明确的其他业务码约定，继续按那些既有约定处理；本题未提供的码不能被自行归为确定业务失败。

运行时读取从 `unknown` 开始，局部检查信封和字段即可，不安装校验依赖，不用 `raw as ReasonsResponseDto` 掩盖缺项，也不要求全对象校验通过才承认已知成功码。原始 DTO 与功能视图表达不同边界；若工程已有生成契约或 Schema，则更新该源并派生类型，不额外维护上述手写副本。

例如输入：

```ts
{ code: 200, data: [{ id: 'R1' }, null, { id: 'R2', name: '其他' }] }
```

读取成功，选项保持三条及原顺序，功能视图为：

```ts
[
  { id: 'R1', label: undefined },
  { id: undefined, label: undefined },
  { id: 'R2', label: '其他' },
]
```

交互使用 `option.label ?? ''` 空显示，不过滤缺名称条目，不去重，不增加“异常条数”，也不因 `null` 拒绝整页。实际 `data: []` 表示成功且本页无记录；成功码下没有可读取数组时，保留 `options: undefined`，展示“暂无列表数据”，不能把它改判为接口失败或解释为业务无匹配。

原因选择、保存与最终完成继续由现有完成场景协调。读取函数不保存、不完成、不预选第一个原因。缺少显示名称但含真实 `id: 'R1'` 的条目仍保留；是否提交取决于用户实际选择，而非名称是否非空。没有真实标识的空行不能触发保存；展示索引、空字符串占位和临时 key 均不能充当原因标识。场景保存前至少沿用以下必要检查：

```ts
// 位于已有场景的保存操作中；selectedReason 必须来自用户选择。
if (!selectedReason?.id) {
  // 使用场景既有提示机制展示“请选择有效的原因”，停止该次保存。
  return;
}

// 后续仍由原场景调用原保存入口，提交 selectedReason.id 的原值，
// 再按原流程协调最终完成；readReasons 不参与这些副作用。
```

不把 ID 转成显示名，不生成替代 ID，不回退到第一条，不额外猜测 ID 格式。公共 HTTP、认证、传输异常和取消处理均沿用现有协议；不要捕获这些异常后伪造原因列表成功。

**验证范围按这两条实际调用链分别确定。**

| 改动 | 类型检查之外必须验证的行为 | 本批消费者与接线范围 |
| --- | --- | --- |
| A：移动类型和默认常量 | 缺省数量为 `1`；显式数量包括 `0` 透传；URI 去重顺序；空结果；SDK 错误与取消透传；并发调用的控制器和 Map 不共享；使用传入的 SDK 实例 | 能力行为测试，以及照片选择、头像选择、H5 图片选择桥的相关调用、结果和取消回传用例；核对 bootstrap 继续提供实际 SDK，公开入口和平台解析未改变 |
| B：`name` 到原显示字段的适配 | 只有数值 `200` 确认成功；字符串 `'200'`、缺码、未知码不确认成功；缺名称、`null`、重复条目仍保留数量和顺序；空数组与无可读取列表区分；无旧字段偷偷回退；缺展示值不改判失败 | `readReasons` 的适配契约测试和唯一消费者——完成场景的原因选择交互；验证中文空显示、无自动选择、无读取触发保存、有真实用户选择后传原始 ID，以及最终完成仍由场景协调 |

工程内测试沿现有组织放到 `__tests__/capabilities/imagePicker/pickImage.test.ts`、`__tests__/domains/marketing/reasons/readReasons.test.ts`，消费者使用各自已有测试文件；测试专用 fixture 就近放置。本次未提供消费者的真实文件名，不杜撰路径。静态引用检查用于核对导入和公开出口，另补 H5 协议与宿主接线的非静态关系，不能只凭 TypeScript 或相关测试选择命令宣称影响已全部覆盖。

本批 A 已有 H5 消费者，所以它的相关契约回归现在就属于范围；原生初始化没有变化，不要求为文件拆分默认重跑所有设备能力或整个营销领域。B 的实际消费者只有完成场景，没有依据扩大到 H5 或其他能力。

未来以下变化才需要相应扩大验证：

- A 的公开默认数量发生变化：验证三个现有消费者对数量的语义，包括 H5 的默认回传行为；这不是一次只有编译检查的常量替换。
- `pickImage` 的公共输入、结果、取消协议或 H5 桥序列化改变：扩大到对应入口、桥协议、宿主与跨仓消费者的契约验证。
- SDK 版本、原生配置、权限、bootstrap 初始化或资源生命周期改变：增加相关平台构建、真机和宿主生命周期验证；Web 支持范围或平台适配改变时，验证对应 Web 接入。
- B 的功能公共结果、真实原因标识或保存职责改变，或出现新的 H5、Agent 等消费者：先核对对应契约和场景职责，再验证那些实际消费者。公共 HTTP、认证或取消协议变更时，再扩大到其实际依赖能力。
- 静态引用与人工核对发现共享依赖或遗漏调用关系：扩大到受影响组合并修正验证范围。仅仅同处一个目录或领域不是全量回归的理由。

**本次已执行与未执行。**

已在 Node.js v24.13.0 中运行独立的 JavaScript 断言脚本 `after-capability-check.mjs`，进程退出码为 `0`。它验证了上面图片算法与私有原因适配核心，包括默认值、显式 `0`、去重顺序、空数组、并发隔离、SDK 拒绝对象透传、严格业务码、缺值与 `null` 条目、重复标识、无数组数据和新字段映射。

该脚本是隔离的算法验证，没有载入真实工程，也未编译上述 TypeScript。未执行真实工程类型检查、导入约束检查、场景 UI 测试、H5 桥测试、bootstrap 接线测试、平台构建、真机或 CI；未安装依赖、未调用真实设备或业务服务、未编辑真实工程。上述工程验证均是本批接入时应完成的范围，不能据隔离脚本通过宣称端到端功能已验证。
