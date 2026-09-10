本批按提供的 `portal-development` 技能及包内开发规则第 2—5 节、工程组织第 3—6 节处理。A 是已有能力的等价整理，B 是既有领域读取功能的响应适配；两者不改变公开操作名称，也不引入新的提交行为。

## A. 图片选择能力

最小组织如下；保留已有 `pickImage.ts` 公开路径，不强制增加 barrel 或平台文件：

```text
capabilities/imagePicker/
  pickImage.ts
  types.ts
  constants.ts
__tests__/capabilities/imagePicker/pickImage.test.ts
```

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

只有 `DEFAULT_LIMIT` 是固定默认配置值。`controller`、`chosen`、`limit`、`files` 保持每次调用的局部作用域；`sdk` 保持传入实例。不能因它们使用 `const` 就移出函数，也无需增加共享 `state.ts`、类或容器。保留 Map 的首次插入顺序和去重结果，不顺手更换结果处理算法。

bootstrap 继续提供实例并向现有消费者接线，调用方向为 `app/bootstrap → 消费者/能力公开入口`；消费者调用 `pickImage(input, sdk)`。能力不导入 bootstrap，不从全局 `config/sdk.ts` 获取运行期实例。原有宿主初始化与释放责任保持不变。`PickInput`、`PickerSdk` 及默认值若已有公开出口，维持兼容并只在实际需要的出口重导出，不自动公开全部内部类型。

取消语义以题设代码为准：每次创建新的 signal 传给 SDK，SDK 的拒绝直接向上传播。本批不新增外部取消参数、不捕获取消后返回空数组，也不在 `finally` 中额外 abort。原生及 Web 的既有支持范围保持不变；如果 Web 原先不支持设备选择，继续按原有协议表达不支持，不能伪造“选择成功”。题设没有给出原有 Web 返回/错误协议，因此不编造一个替代实现。

A 的定向验证：

- 替代 SDK 记录入参：省略 limit 时仍为 `1`；显式 limit 原样传递，包括 `0`，证明 `??` 没有被换成 `||`。默认值应有独立语义断言，不能只把期望值也引用 `DEFAULT_LIMIT`。
- 两个并发调用收到不同的 signal；各自使用不同的 SDK 替身和返回值，结果没有串扰。验证实际 URI 列表，而不只断言 SDK 被调用。
- SDK 返回 `['u1', 'u2', 'u1']` 时结果为 `['u1', 'u2']`；返回 `[]` 时仍为 `[]`；SDK 的普通错误与取消拒绝保持原有传播语义，例如断言同一个拒绝对象向上传播。
- 核对生产方与照片选择场景、头像选择、H5 图片选择桥的公开导入和实际接线。保留或运行这三个消费者相关的定向用例，尤其检查桥接请求参数、结果及取消映射；H5 已是实际消费者，不能因静态引用未识别协议关系而忽略它。
- 核对原有宿主与 Web 平台解析仍接入正确实现，不把测试替身装入生产 Web 文件。类型检查和导入方向检查不能代替这些行为断言。

本批没有 SDK、原生配置或平台支持变化，不因此扩成全设备能力或全营销领域测试。未来若改变默认数量，即使类型不变，也需验证三个消费者中依赖默认数量的行为；若改变公开输入输出、取消、URI 语义或路径，需覆盖对应消费者与 H5 协议；若改变宿主生命周期、SDK 初始化、原生依赖或 Web 支持，再补对应宿主、多实例、卸载、平台构建、设备及 Web 接入验证。其他能力仅在确有共享依赖或契约影响时纳入。

## B. 原因读取适配

保留 `domains/marketing/reasons/readReasons.ts` 的既有公开名称、签名、功能结果与错误通道。原始 DTO、所属接口的成功码和映射由该功能的适配器维护，页面只消费已映射的功能结果。最小组织示例：

```text
domains/marketing/reasons/
  readReasons.ts                 # 既有读取入口，保持原有请求接线
  types.ts                      # 既有功能结果类型
  adapter/
    types.ts                    # 该接口原始响应的已知字段
    constants.ts                # 仅该接口本批用到的成功码
    mapReasonsResponse.ts       # 集中检查、映射响应
__tests__/domains/marketing/reasons/
  readReasons.test.ts
  mapReasonsResponse.test.ts
```

若现有适配器已经有对应位置，直接在该处修改，不为上述示意目录迁移无关文件。无需新建全局 `types/` 或 `config/`，也不复制全部接口码表。既有小型公开入口仅继续导出 `readReasons` 与消费者实际需要的功能类型，适配 DTO 不进入公共出口。

以下用 `ReasonOption.label` 表示题设中既有的可选显示字段；实际工程沿用其原有名称和类型，不因示例改名。标识始终保留真实响应 id。

`reasons/types.ts` 中的功能结果示意：

```ts
export interface ReasonOption {
  id: string;
  label?: string;
}
```

`adapter/types.ts` 保留外部字段 `name`，在未验证边界使用 unknown：

```ts
export interface ReasonsResponseDto {
  code?: unknown;
  data?: unknown;
}

export interface ReasonDto {
  id?: unknown;
  name?: unknown;
}
```

`adapter/constants.ts`：

```ts
export const READ_REASONS_SUCCESS_CODE = 200;
```

`adapter/mapReasonsResponse.ts` 的关键转换逻辑：

```ts
import type { ReasonOption } from '../types';
import { READ_REASONS_SUCCESS_CODE } from './constants';
import type { ReasonDto, ReasonsResponseDto } from './types';

export function mapReasonsResponse(raw: unknown): ReasonOption[] {
  if (raw === null || typeof raw !== 'object' || Array.isArray(raw)) {
    throw new Error('Invalid reasons response');
  }

  const response = raw as ReasonsResponseDto;
  if (response.code !== READ_REASONS_SUCCESS_CODE) {
    throw new Error('Read reasons failed');
  }
  if (!Array.isArray(response.data)) {
    throw new Error('Invalid reasons data');
  }

  const options: ReasonOption[] = [];
  for (const value of response.data) {
    if (value === null || typeof value !== 'object' || Array.isArray(value)) {
      continue;
    }
    const item = value as ReasonDto;
    if (typeof item.id !== 'string' || item.id.length === 0) {
      continue;
    }
    options.push(
      typeof item.name === 'string'
        ? { id: item.id, label: item.name }
        : { id: item.id },
    );
  }
  return options;
}
```

上述代码采用题设示例的字符串标识形态；实际 id 类型以原有功能契约为准，不另做字符串化。错误抛出位置展示的是失败分支，具体错误类型及公开失败结果必须复用原有适配错误通道；题设未提供该通道，不能用示例中的普通 Error 替换已存在的公开错误协议。

`readReasons` 内保持已有 HTTP 调用、凭证与取消接线，只把原来处理 `label` 的映射替换为 `mapReasonsResponse(raw)`，将其结果按原有功能结果结构返回。请求参数、URL、HTTP 客户端接口未给出，因此不补造新的调用签名或端点。若现有边界已有 Schema/生成契约，则更新其源并由 `types.ts` 派生类型，上述手写 DTO 不与它并存。

关键语义：严格以数值 `200` 判定成功，`'200'` 不通过，不依赖 truthy 或隐式转换。`{ id: 'R1' }` 保留为没有显示字段的真实选项，`null` 被安全忽略；不因为没有 name 就删除有真实 id 的条目，也不制造 label 或 id。缺少真实标识的条目不成为可提交选项。有效空数组与失败响应分别处理，失败不能伪装成成功空列表。

选择状态继续由完成场景维护：读取结果不自动选中首项；缺名称也不能触发默认选择。用户实际选择一个选项后，场景保留该选项的真实 id，沿既有交互和确认规则协调保存及最终完成。`readReasons` 只读取，不保存、不自动完成，适配器也不承接这些副作用。

B 的定向验证：

- `{ code: 200, data: [{ id: 'R1', name: '原因一' }] }` 映射为原有功能结果形态，显示字段为“原因一”，id 为 `R1`；确认唯一消费者无须自行了解 `name`。
- 混合数组 `[{ id: 'R1' }, null, { id: 'R2', name: '原因二' }]` 不崩溃，保留 R1 的无显示字段结果及 R2 的名称和真实 id。额外覆盖缺 id 条目，确保没有生成索引、名称或占位符标识。
- 数值 `200` 成功、字符串 `'200'` 与其他未确认码失败；非数组 data 走既有失败通道；有效 `[]` 保持成功空列表。验证实际结果和错误分支，不能只检查静态 DTO 类型。
- 完成场景的原因选择交互在名称缺失时仍能安全呈现，读取完成后没有自动选择、保存或最终完成。用户明确选择 R2 后，场景保存参数必须是 `R2`；未选择时不替用户填入 R1。UI 缺名称的显示沿用既有规则，不趁适配新增产品文案或交互。
- 用替身验证读取调用次数、保存和最终完成在“只读取”阶段均为零；核对原有 HTTP、认证、取消与失败传播接线未改变。运行映射、读取入口及唯一消费者的相关行为用例和类型检查。

B 当前只有完成场景的原因选择交互这一消费者，不扩展到 H5、宿主或其他设备能力。未来只有新增这类消费者、改变公共结果/错误/取消契约、修改共享 HTTP/认证协议或引入实际宿主依赖时，才沿真实依赖扩大验证；若要把保存并入读取或改变确认责任，则属于新的行为和场景职责设计，需先明确需求与契约，不能当作本次字段映射顺带实施。

## 验证证据边界

本次仅阅读题设与指定技能资料，形成书面实现及定向验证方案；未修改合成工程源码、未运行类型检查或测试、未安装依赖、未请求真实 SDK 或业务系统。以上用例是应执行的验证范围，不是已通过的测试记录。工程现有 TypeScript、ESLint 与导入检查可执行确定性的规则；技能文本本身不证明这些规则已在工程或 CI 强制运行。
