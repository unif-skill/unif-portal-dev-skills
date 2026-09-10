两个改动都保留已有公共名称和功能语义。A 将固定默认值与类型移到能力内部的角色文件，运行期资源继续按每次调用创建；B 在原因查询所属适配处完成 `name → label` 映射，由完成场景继续负责选择、保存和最终完成。

本方案依据所提供的 `portal-development` 文件角色、依赖方向和验证规则，以及 `architecture-design` 的功能职责、业务结果与影响范围规则。以下路径均表示题目的合成工程，未编辑真实工程。

**A. 图片选择能力**

最小文件组织：

```text
src/capabilities/imagePicker/
  pickImage.ts       # 保留公开函数名；操作与调用局部资源
  types.ts           # PickInput、PickerSdk 与 SDK 调用参数
  constants.ts       # DEFAULT_LIMIT = 1
```

`pickImage.ts` 继续作为明确的公开文件。已有 `index.ts` 时只维护必要的具名导出，不新建全能力总出口；显式类型从公开文件导出，避免消费者读取私有类型文件。`DEFAULT_LIMIT` 保持原来的公开范围，不能因为迁入 `constants.ts` 就扩大公开面。

```ts
// src/capabilities/imagePicker/types.ts
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

这些是本题给定 SDK 契约的手写类型整理。如果真实 SDK 已提供这些公开类型，应直接引用或派生 SDK 类型，避免另维护一份接口定义。

```ts
// src/capabilities/imagePicker/constants.ts
export const DEFAULT_LIMIT = 1;
```

```ts
// src/capabilities/imagePicker/pickImage.ts
import { DEFAULT_LIMIT } from './constants';
import type { PickInput, PickerSdk } from './types';

export type { PickInput, PickerSdk } from './types';

export async function pickImage(
  input: PickInput,
  sdk: PickerSdk,
): Promise<string[]> {
  const controller = new AbortController();
  const chosen = new Map<string, number>();
  const limit = input.limit ?? DEFAULT_LIMIT;
  const files = await sdk.pick({ limit, signal: controller.signal });
  files.forEach((uri, index) => chosen.set(uri, index));
  return Array.from(chosen.keys());
}
```

这里只移动类型和固定默认值，保留原算法及两个参数的调用契约：

- `controller`、`chosen` 属于本次操作；`limit` 依赖本次输入；`files` 是本次 SDK 结果，都留在函数内。`const` 不等于固定常量，不能搬到 `constants.ts`。
- SDK 实例由现有 bootstrap 创建或取得，沿现有接线显式传入调用者。调用仍为 `pickImage(input, sdk)`；能力不导入 `app/bootstrap`，SDK 实例不放全局 `config/sdk.ts`，也不增加注册中心或 DI 容器。
- 保留 `??` 的含义：未提供数量时为 `1`；显式传入 `0` 仍传递 `0`，本批不新增限额校验、取整或重试。
- 每次调用传入各自的 `AbortSignal`。原片段没有公开取消入口，也没有主动调用 `abort()`；本批不新增外部取消参数、不改变 SDK 拒绝结果、不把取消转换为成功或空列表。
- 保留 URI 去重及首次出现顺序。例如 `['a', 'b', 'a']` 返回 `['a', 'b']`。空数组仍为空数组。

照片选择场景、头像选择和 `integrations/h5` 图片选择桥都继续复用 `pickImage`。H5 桥负责协议输入与回包适配，不另写设备选择算法；H5 页面仍承担原业务流程。

本批不新增 Web 版本。已有 Web 实现与支持范围保持原样；只有确有平台差异时才使用 `pickImage.web.ts` 等平台文件。Web 不支持的操作应继续通过既有契约表达支持范围，不能直接返回“选择成功”，更不能把测试替身放进正式 Web 实现。原生宿主的初始化和资源责任也沿用现有接线。

**A 的定向验证范围（待执行）**

在 `__tests__/capabilities/imagePicker/pickImage.test.ts` 测试真实 `pickImage`，仅替换 SDK：

1. 缺省数量准确传入 `1`，显式数量原样传入；包含 `0` 用例以验证没有误用 `||`。
2. SDK 每次调用一次；空列表、普通列表、重复 URI 的返回值与顺序保持一致。
3. 两次并发调用的 `signal` 引用不同，返回结果互不混入；控制器初始未取消。SDK 拒绝，包括既有取消对应的拒绝，继续向调用方传播。
4. 核对三个真实消费者的导入、参数传递和结果处理；必要时以现有场景/桥接测试验证照片选择、头像选择与 H5 桥仍使用同一个能力。H5 协议关系须显式核对，不能只依赖 TypeScript import 检索。
5. 类型、导入边界和现有静态规则检查；若路径调整影响 Web 解析，补 Web 入口构建或导入检查。由于本批没有原生 SDK、宿主或平台行为变更，不据此要求所有设备能力真机回归。

未来若将默认数量从 `1` 改为其他值，虽然函数类型不变，仍须验证上述三个消费者的实际数量、UI 限制和 H5 回包语义。若改变取消、URI 结果、权限、SDK、宿主初始化或平台支持，则扩大到相应消费者及接线；涉及原生行为时补对应平台构建和真机验证。只有共享设施或其他能力的实际依赖受影响时才扩到其他能力。

**B. 原因选项查询的领域适配**

本批适配继续归属 `domains/marketing/reasons`。后端仅改原始字段，Portal 仍提供原来的原因选项语义；页面不需要各自识别 `name` 或解析业务码。

```text
src/domains/marketing/reasons/
  readReasons.ts    # 保留公开查询；原请求接线和所属响应适配
  types.ts          # 公共选项与该适配器私有原始类型
  constants.ts      # 本接口已确认的成功码
  index.ts          # 若已有，则继续仅导出 readReasons 和必要公共类型
```

如果现有单元已将适配器独立为子目录，以上原始 DTO、业务码和映射继续留在该适配子单元的 `types.ts`、`constants.ts` 与实现文件；本批不为分类再搬一次。没有已有拆分时，映射先作为 `readReasons.ts` 的私有普通函数即可。

原始 DTO 和码表不能移到全局 `types/`、`config/`。公共 HTTP 继续负责既有传输、认证和取消处理，不认识这个业务成功码。原始类型只供适配器内部使用，不通过公共 `index.ts` 暴露。

下面代码说明本批的读取投影。题目未给出 `readReasons` 已有参数、完整结果联合和错误分支，所以不假定或替换其公共结果形状；`ReasonOption` 仅用来说明既有选项视图需要允许缺失字段，真实类型名称沿用原工程。

```ts
// src/domains/marketing/reasons/types.ts
// 功能读取视图：字段允许实际缺失。
export interface ReasonOption {
  id?: string;
  label?: string;
}

// 原始协议描述接口应提供的字段，不把它强制套到全部实际行。
// 这两个类型仅在本单元内部使用。
export interface RawReasonDto {
  id: string;
  name: string;
}

export interface RawReadReasonsResponse {
  code: number;
  data: RawReasonDto[];
}
```

```ts
// src/domains/marketing/reasons/constants.ts
export const READ_REASONS_SUCCESS_CODE = 200;
```

```ts
// src/domains/marketing/reasons/readReasons.ts 内的私有辅助
import type { ReasonOption } from './types';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function mapReasonOptions(data: unknown): ReasonOption[] | undefined {
  if (!Array.isArray(data)) return undefined;

  return Array.from(data, (row): ReasonOption => {
    if (!isRecord(row)) return {};

    return {
      id: typeof row.id === 'string' ? row.id : undefined,
      label: typeof row.name === 'string' ? row.name : undefined,
    };
  });
}
```

`Array.from` 保留条目数量和顺序，不过滤缺值行；实际 `null` 行投影为空选项行。显示层使用 `option.label ?? ''`，缺失身份仍为缺失身份。这里按本题字符串标识读取，不把行号、显示文本或默认值补成原因 ID，也不将原始 `name` 改回线上 `label`。

`readReasons` 中的响应分支按下列连接方式调整。代码框为接入既有函数的伪代码，`既有…` 表示题目未提供、需保持的原有实现，不是要求新增函数或结果状态：

```text
response = await 既有请求(原输入、原认证、原取消参数)
rawCode = 安全读取 response.code

if rawCode === READ_REASONS_SUCCESS_CODE:
    options = mapReasonOptions(安全读取 response.data)
    return 既有成功结果(options)

return 既有非成功码解释(rawCode, 所属请求诊断)
```

数值 `200` 是本题唯一已确认成功码。字符串 `'200'`、缺码和未知码都不能转换为成功，也不能仅因不是 `200` 就武断判为某个已知业务拒绝；其他状态沿用已确认的原接口解释，保留原始码用于请求诊断。本题没有提供其他码表，不编造码值与文案。传输异常和取消继续沿既有协议处理，不在字段映射中吞掉。

成功码下的结果处理应明确区分：

| 原始响应内容 | 功能结果与交互 |
|---|---|
| `{code:200,data:[{id:'R1',name:'缺货'}]}` | 成功，选项投影为 `{id:'R1',label:'缺货'}` |
| `{code:200,data:[{id:'R1'},null]}` | 成功，两行都保留；第一行保留真实 `R1`，显示字段为空；第二行身份和显示字段均缺失 |
| `{code:200,data:[]}` | 成功，本次列表明确为空 |
| `{code:200}` 或 `data:null` | 成功，但无可读取的列表数据；展示“暂无列表数据”，不推断业务无匹配 |
| `{code:'200',data:[...]}` | 不确认成功；有数据不能替代已确认的业务码类型 |
| 缺码、未知码或传输失败 | 依各自既有语义处理，不伪造选项或成功结果 |

本批不将缺失展示字段改判为接口失败，不整页拒绝、不过滤条目、不增加异常条目计数，也不引入“成功但回执异常”状态。若既有读取视图不能表达缺字段或没有列表数据，应在所属结果类型的可选性中准确表达；这属于功能契约需要同步消费者的部分，不能只用类型断言掩盖。未知的既有完整结果结构在接入前核对，不直接套用新的公共联合类型。

唯一消费者是完成场景的原因选择交互。它展示查询快照，维护用户选择；初始值不能根据第一个原因、缺少名称或查询成功而自动设置。保存时从用户明确选中的条目取得真实 `id`，身份缺失则提示选择有效原因并停止后续写入。有真实 `R1` 但名称缺失的行仍保留 `R1`，不因展示为空自行删除；查询也不替用户决定选用它。

完成场景继续按已有确认和调用顺序协调保存原因与最终完成。`readReasons` 不调用保存或最终完成，不新增确认、重试、缓存或业务请求。成功读取选项不能证明保存成功，保存成功也不能直接代表最终完成成功。

**B 的定向验证范围（待执行）**

测试真实 `readReasons` 或其现有适配入口，替换 HTTP 外部边界，不能仅测试一份脱离调用链复制出来的映射函数：

1. 用新原始字段 `name` 验证输出仍是既有可选显示字段语义；消费者无需读取原始 DTO。
2. 精确断言数值 `200` 与字符串 `'200'` 不等价；覆盖缺码、未知码与传输异常，非成功不能凭 `data` 非空变成成功。
3. 成功响应中的 `{id:'R1'}` 和 `null` 保留行数和顺序，不抛全列表校验错误；缺少名称按空显示，真实 ID 保持原值。
4. 分别验证真实空数组与无可读取列表数据的区别，二者都不因缺数据改判接口失败。UI 提示与业务含义一致。
5. 对唯一完成场景验证：读取不调用保存或完成；没有用户选择不默认选第一项；选择缺少 ID 的行不发起写入；明确选中有效原因时使用该行真实 ID，保持既有保存和最终完成顺序与结果处理。
6. 保留现有认证、取消接线的相关回归；若本批只改映射，不修改和重跑整个公共 HTTP 实现。运行必要类型、公开导出与导入边界检查。

此次字段变动优先覆盖原因适配及唯一完成场景的必要交接，不自动扩到 H5、宿主或其他能力。未来若原因功能的公共输入输出、成功/失败语义或写入职责发生变化，应先重新明确契约与确认责任，再覆盖真实生产方、消费者及组合；若 H5 开始消费该功能或其桥协议改变，则新增 H5 链路验证。若修改公共 HTTP、认证或取消协议，则扩大到受影响调用方。只有改到原生宿主、平台适配或共享设备设施时，才涉及相应构建、设备或其他能力验证。

**已执行与未验证**

本次已通过指定读取器读取样本、两个技能及适用的规范章节，并据此完成以上设计与代码片段；完整答案已保存到指定输出文件。未读取或修改真实工程，未安装依赖，未执行 TypeScript、单元测试、CI、Web/原生构建、设备操作或真实业务请求。上述验收项均为待执行范围，代码片段不能作为已通过测试的证据。
