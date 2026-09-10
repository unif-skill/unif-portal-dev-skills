# 设备与领域适配的定向修改

依据题设及指定版本的 portal-development 开发规则第 2—5 节、工程组织第 4—5 节，以及 architecture-design 平台规范第 6—7 节。以下是书面改动方案；没有安装依赖、访问 SDK/业务系统或执行工程测试。

## A. imagePicker：等价整理

保留 `capabilities/imagePicker/pickImage.ts` 的公开操作 `pickImage(input, sdk)`、返回 URI 数组及原有异常传播语义。最小文件组织为：

```text
capabilities/imagePicker/
  pickImage.ts     # 继续作为明确的公共文件
  types.ts         # PickInput、PickerSdk 及 SDK 调用参数
  constants.ts     # DEFAULT_LIMIT
```

无需为拆分另建状态文件、SDK 全局配置或总 barrel；已有小型公共出口则同步其现有导出。`PickInput` 与 `PickerSdk` 如有消费者仍从原文件导入，可在原公开文件做具名类型重导出以保持兼容。

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

// capabilities/imagePicker/constants.ts
export const DEFAULT_LIMIT = 1;

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

只有默认数量是命名固定值。controller、chosen 是每次调用的资源和状态；limit、files 是本次调用计算和获得的数据；sdk 是外部提供的运行期实例。这些变量不会因为使用 `const` 就成为固定常量。Map 保持原算法：同 URI 去重，返回顺序按首次插入顺序，不因后续重复项更新 index 而改变。

bootstrap 继续持有并提供实际 SDK；能力不导入 `app/bootstrap`，也不从 `config/sdk.ts` 找全局实例。现有组装处可沿用普通参数或已有绑定方式，把同一个已提供的 SDK 接入照片选择、头像选择及 H5 图片选择桥。例如组装作用域中的 `const pick = (input: PickInput) => pickImage(input, sdk)` 可以传给现有消费者；这只是接线示意，不新增工厂 API 或注册框架。

没有公开取消入口的事实保持不变：本次仍为每次 SDK 调用创建独立 signal，不新增 abort 时机、不吞掉 SDK 的取消拒绝、不将取消转换成空数组或成功。Web 继续采用现有支持边界：真实可用的现有实现保持；不支持的平台继续明确表达不支持。题设未提供现有 Web 错误协议，不能编造新状态值，也不能直接返回“选择成功”。原生宿主与平台实现本批不新增、不替换。

验证范围：

- 静态核对文件拆分后的相对导入、原公开文件及类型导出、bootstrap 到能力的依赖方向；查明三个实际消费者的静态导入及 H5 协议关系。
- 测试真实 `pickImage`，仅替换 PickerSdk：缺省 limit 为 1，显式 limit 原样传入（包括现有 `??` 对 0 的处理），空数组返回空数组；重复 URI 去重且首次出现顺序不变。
- 两次并发调用分别取得不同 signal 和独立 Map，结果不串扰；SDK 拒绝及取消拒绝原样传播；没有新增重试或额外 SDK 调用。不能把“存在 signal”说成“用户取消已经接通”。
- 照片选择、头像选择和 H5 图片选择桥验证实际公开入口接线、结果及原有取消/错误映射。H5 是本能力已知消费者，本批就应覆盖其受影响接线，无需等待未来变化。
- 默认数量本批保持 1。未来修改其值属于可观察行为变化，应覆盖三个消费者未传 limit 时的数量及交互预期；公开签名、结果或错误语义变化同样扩到全部实际消费者。
- 只有 SDK/原生行为、权限、宿主生命周期或平台支持范围改变时，增加相关平台构建、宿主和真机验证；共享设备接口或公共支持能力变化才扩到依赖它的其他能力。单纯拆文件不默认要求全领域或所有设备能力回归。

## B. reasons：字段变化收敛到所属适配边界

保留 `domains/marketing/reasons` 单元和 `readReasons` 公开名称及只读语义。唯一消费者继续是完成场景的原因选择交互；保存原因与最终完成继续由场景协调，读取或映射过程没有保存调用。

在现有同职责文件中修改即可；若当前没有单独的适配文件，最小组织可以是：

```text
domains/marketing/reasons/
  readReasons.ts       # 已有公共读取入口
  types.ts             # 已有功能公共结果和选项类型
  adapter/
    mapReasons.ts      # 原始码解释与 name → 已有显示字段的映射
    types.ts           # 此接口原始 DTO、容缺读取视图
    constants.ts       # 此接口明确的数值成功码 200
```

`adapter` 是单元内普通实现子单元，名称以工程已有适配目录为准，不为本题另建顶层框架。原始 DTO 和该接口的码值留在适配边界；公共 types 只表达功能语义，不暴露后端信封。页面不解析 code，不自行将 name 映射为显示字段；全局 `types/` 与 `config/` 不接收这些内容。不收集尚未提供的“全部码表”。若原契约由 Schema 或生成代码维护，修改其源并重新生成，不再复制手写 DTO。

以下代码展示必要映射逻辑。题设未给出 `readReasons` 的参数、完整结果分支名称和现有显示字段名，因此 `ReasonOption`、`label`、`success/unconfirmed` 是书面示意，落地时复用已有公共名称与分支；不能以示例为依据替换已确认契约。示例以 label 表示原有可选显示字段。

```ts
// adapter/types.ts：原始应有结构与实际读取视图区分
export interface ReasonDto {
  id: string;
  name: string;
}

export interface ReasonsResponseDto {
  code: number;
  data: ReasonDto[];
}

export interface ReasonReadView {
  id?: unknown;
  name?: unknown;
}

export interface ReasonsResponseReadView {
  code?: unknown;
  data?: unknown;
}

// reasons/types.ts：对应已有功能语义；分支命名需沿用项目契约
export interface ReasonOption {
  id?: string;
  label?: string;
}

export interface ReasonsSuccess {
  status: 'success';
  options?: ReasonOption[];
}

export interface ReasonsUnconfirmed {
  status: 'unconfirmed';
}

export type ReasonsResult = ReasonsSuccess | ReasonsUnconfirmed;

// adapter/constants.ts
export const REASONS_SUCCESS_CODE = 200;

// adapter/mapReasons.ts
import { REASONS_SUCCESS_CODE } from './constants';
import type { ReasonReadView, ReasonsResponseReadView } from './types';
import type { ReasonOption, ReasonsResult } from '../types';

function mapReason(raw: unknown): ReasonOption {
  const item: ReasonReadView =
    raw !== null && typeof raw === 'object' && !Array.isArray(raw)
      ? raw
      : {};
  return {
    id: typeof item.id === 'string' ? item.id : undefined,
    label: typeof item.name === 'string' ? item.name : undefined,
  };
}

export function mapReasons(raw: unknown): ReasonsResult {
  const response: ReasonsResponseReadView =
    raw !== null && typeof raw === 'object' && !Array.isArray(raw)
      ? raw
      : {};

  if (response.code !== REASONS_SUCCESS_CODE) {
    // 未提供其他已确认码，不猜测具体业务拒绝；沿用现有未确认结果。
    // 如已有确定失败码，仍按原有准确分支解释。
    return { status: 'unconfirmed' };
  }

  return {
    status: 'success',
    options: Array.isArray(response.data)
      ? response.data.map(mapReason)
      : undefined,
  };
}
```

`readReasons` 保持已有请求参数、HTTP 客户端、凭证和取消参数转交，只把原有响应解释替换为上述映射；等价结构是 `return mapReasons(await existingReadRequest(...existingArgs))`，此处不是新增请求 API。传输失败保持既有处理，不以空选项覆盖错误。请求诊断沿用已有记录位置保留原始 code 及请求关联，既不能将 `'200'` 强制转数值，也不要求消费者再判断它。

数值 `200` 已证明接口成功；展示缺项不把它改判失败。映射使用 map 而非 filter：`[{id:'R1'}, null]` 仍得到两个同序条目，分别为 `{id:'R1', label:undefined}` 与 `{id:undefined, label:undefined}`。交互用 `label ?? ''` 空显示，不补造名称、原因标识或异常条数。实际空数组是无记录；没有可读取数组时保留 options 缺失，展示“暂无列表数据”，不能据此断言业务无匹配。

完成场景把“读取成功”“可展示内容”“已选择可保存身份”分别处理。初始化仍无用户选择，禁止因为缺少名称而默认选择首项。用户明确选择了真实 `R1` 时，即使该行名称缺失，也不能仅因缺展示字段禁止有效身份的既有操作；null 行没有真实 id，不能进入保存。空字符串、缺失 ID 等不满足保存输入时，按现有交互提示补齐选择，不能以数组下标、显示空值或其他行的 ID 代填。代码中即使使用位置作为纯 UI key，也不能把它提交成 reasonId。

场景保存前的必要判断可表达为：

```ts
// 位于既有完成场景中，selected 仅由用户选择事件设置。
const reasonId = selected?.id;
if (typeof reasonId !== 'string' || reasonId.length === 0) {
  // 沿用场景的“请选择原因”提示；不保存、不执行最终完成。
  return;
}
// 在既有确认与调用顺序下，使用真实 reasonId 调用原保存操作。
// 保存与最终完成仍按各自结果契约处理，不在 readReasons 中触发。
```

以上不新增自动确认、重试、缓存或提交顺序，也不假设保存成功即最终完成成功。题设未给出保存和完成接口，所以不编造它们的参数及回执。

验证范围：

- 适配契约测试使用真实 `mapReasons` 与真实读取入口，替换网络边界：数值 200、字符串 `'200'`、缺码和未知码分别处理；即使存在非空 data，也不能把未知码当成功；已有确定失败分支保持。
- 验证新 name 字段映射后功能公开结果语义不变；不要求页面适应后端改名。测试缺 name、null 行及正常行混排，断言数量、顺序和每行实际 id；不剔除缺值条目。
- 区分 `data: []`、data 缺失及不可读取数组；在成功码下均保持成功，展示分别符合“无记录”和“暂无列表数据”的语义。不能仅测类型可赋值。
- 完成场景的原因选择测试覆盖未选择不保存、不默认选首项、用户选择真实 R1 后转交真实 ID、无 ID 行不保存，以及中文空显示/提示。断言只读取不触发保存和最终完成，既有确认与调用顺序不变；其他完成场景步骤仅覆盖受影响组合，不重做无关能力测试。
- 验证既有 HTTP、认证及取消转交没有改变，取消/失败不被映射成成功或自动选择；本批没有修改公共传输层，因此不默认扩大到所有接口。
- 本批主要覆盖 reasons 适配、公开读取入口与唯一原因选择消费者。B 没有已知 H5 或设备消费者，不因 A 涉及 H5 就扩大 B 的测试。
- 未来公共结果、公开位置/名称或选择/保存职责改变时，重查全部实际消费者及组合链路；新增 H5 消费者或改变 H5 协议时覆盖桥接与入口；公共 HTTP、认证、取消或共享状态改变时覆盖其依赖者；引入宿主或设备行为时增加对应平台、宿主和真机证据。影响范围不能完整识别时再扩大到相关领域和集成链路。

本次交付只有以上方案与关键代码，未执行类型检查、行为测试、平台构建、CI 或真实联调；列出的验证是应实施的范围，不是已通过结果。技能规则也不等于目标工程已经配置了自动门禁。
