# 文件组织、关键代码与验证范围

本答复依据 `PORTAL_DEVELOPMENT.md` 第 2—5 节、`PORTAL_STRUCTURE.md` 第 1、3、4、6 节和 `ARCHITECTURE.md` 第 6.1 节。以下为书面修改方案；未读取合成工程的实际源码、执行工程测试或访问 SDK、业务系统。路径以合成工程为准，`<所属查询单元>` 等表示题设未提供的现有位置，不是建议新增目录。

## 1. 从现有 Schema 派生静态类型

最小组织：

```text
src/domains/marketing/orderInput/
├── schema.ts                 # 保持现有唯一可执行契约
├── types.ts                  # 新增所需派生类型
└── index.ts                  # 现有公开入口增加类型导出；没有时建小型入口
```

`schema.ts` 保留项目当前采用的 Zod 导入方式及定义：

```ts
export const orderInputSchema = z.object({
  customerId: z.string(),
  quantity: z.number(),
});
```

`types.ts`：

```ts
import type { z } from 'zod';
import type { orderInputSchema } from './schema';

export type OrderInput = z.infer<typeof orderInputSchema>;
```

这里的包名沿用题设 Zod 的示例写法；目标工程应保持其已采用入口。当前 Schema 无输入输出转换，推导出的类型就是 `{ customerId: string; quantity: number }`。不另写同字段 `interface OrderInput`，也不增加非空、正数等题设未要求的约束。未来若 Schema 引入转换，再依据消费者用途区分输入与输出推导类型。

`index.ts` 仅增加：

```ts
export type { OrderInput } from './types';
```

保持已有且仍被消费的公开导出；本次不因导出静态类型而额外公开 Schema 或内部函数。两个消费者统一经所属单元公开入口取得类型：

```ts
import type { OrderInput } from '@/domains/marketing/orderInput';
```

单一源仍是现有 Schema，运行时校验和模型 Schema 继续走原有产生链路。采用 Zod 是此单元已有选择，不能据此给其他单元补装框架。

验证：定位两个实际类型消费者，运行覆盖生产方和消费者的 TypeScript 检查，验证公开入口解析及类型约束；复用已有 Schema、模型 Schema 生成相关检查确认无运行时结构变化。不新增一套重复字段快照作为契约源。仅增加类型出口不要求访问模型或业务系统。

## 2. trimLabel 的两个独立批次

### 批次 A：只补输入样本，行为不变

```text
src/utils/trimLabel.ts
__tests__/utils/trimLabel.test.ts
```

实现完整保留：

```ts
export function trimLabel(value: string) {
  return value.trim();
}
```

它作为明确的公开函数文件已经可以使用，无须建立目录或空的 `types.ts`、`constants.ts`、`index.ts`。消费者继续从 `@/utils/trimLabel` 导入。单个测试使用的数据随测试维护，例如：

```ts
import { trimLabel } from '@/utils/trimLabel';

test.each([
  ['', ''],
  ['   ', ''],
  [' 名称 ', '名称'],
  ['\t编号\n', '编号'],
  ['名称 编号', '名称 编号'],
  ['x'.repeat(41), 'x'.repeat(41)],
])('trimLabel(%j) -> %j', (input, expected) => {
  expect(trimLabel(input)).toBe(expected);
});
```

最后一个样本确保本批仍只去除两端空白，没有混入下一批的长度限制。使用项目已有测试运行环境运行该文件即可；若生产代码及入口没有变化，不因补样本默认扩大到整个领域测试。

### 批次 B：显式 TrimOptions 与已确认的 40 长度上限

这是另一独立批次，不纳入批次 A 的实现：

```text
src/utils/trimLabel/
├── trimLabel.ts
├── types.ts
├── constants.ts
└── index.ts
__tests__/utils/trimLabel.test.ts
```

`types.ts` 用 `interface TrimOptions` 维护该批已经确认的对象选项字段。题设没有提供字段、可选性或默认值，本答复不补造字段，也不以空接口、任意键索引或 `any` 代替实际契约。

`constants.ts` 的确定内容是：

```ts
export const MAX_LABEL_LENGTH = 40;
```

`trimLabel.ts` 的必要依赖是：

```ts
import type { TrimOptions } from './types';
import { MAX_LABEL_LENGTH } from './constants';
```

此文件维护 `trimLabel(value: string, options: TrimOptions)` 的实现及那个仅由它调用的私有截取辅助函数，辅助函数不导出、不另建目录、不提升为全局工具。`options` 是否可省略、去空白与截取的顺序、长度按何种字符单位计算，应沿用该独立批次的已确认契约；题设不足以给出这些实现细节，不能擅自用 `slice(0, 40)` 决定字符语义。

`index.ts`：

```ts
export { trimLabel } from './trimLabel';
export type { TrimOptions } from './types';
```

`MAX_LABEL_LENGTH` 虽在内部角色文件导出供实现使用，默认不属于单元公共 API。只有实际消费者需要共享同一上限时，才在该小型入口增加 `export { MAX_LABEL_LENGTH } from './constants'`。保持 `@/utils/trimLabel` 这一公开路径，并删除完成迁移后的同名单文件，避免文件和目录并存造成解析歧义。

验证：查找函数、旧实现路径、选项和上限的实际引用，同步受影响的导入与函数调用；运行类型检查、导入规则检查及定向工具测试。测试覆盖已确认的各选项行为、空白处理、长度 39/40/41 的边界及约定的字符计数语义。公开上限若影响表单提示或消费者校验，验证这些消费者与工具使用同一数值及语义。无需直接测试私有辅助函数；通过公开函数覆盖结果即可。

## 3. hook 中的绑定按生命周期归属

最小组织是现有查询单元增加有真实内容的常量文件：

```text
src/<所属查询单元>/
├── useLookup.ts
└── constants.ts
```

`constants.ts`：

```ts
export const MODE_LABELS = { name: '名称', code: '编号' };
```

`useLookup.ts` 从 `./constants` 引入该固定映射，保留原有实例隔离机制和查询逻辑。

| 内容 | 实际位置和生命周期 |
|---|---|
| `client = createClient()` | 属于当前 hook 实例的运行期资源，留在现有实例初始化与释放链路；不改成模块级共享客户端。 |
| `pending = new Map()` | 属于当前实例的运行期可变状态，保留原有实例持有及清理方式；不抽成共享 Map。 |
| `value = props.query.trim()` | 本次调用或渲染依据当前输入得到的局部值，在原逻辑处计算。 |
| `MODE_LABELS` | 不依赖用户、实例或本次调用的固定展示映射，在所属查询单元 `constants.ts` 维护，按固定值使用。 |

`const` 仅约束绑定重新赋值，不能推出共享范围或资源生命周期。题设已说明实例隔离满足要求，本次不改写其 React 生命周期机制，不引入 `state.ts`、store、持久化或 `variables.ts`。若映射只有单元内部消费者，只保持内部导出即可，不增加公共出口。

验证：核对变化只移动固定映射，运行所属 hook 的相关测试与类型检查；验证展示名称和编号保持原样，并复用已有多实例、查询变化、卸载清理测试确认原隔离与释放行为没有受损。无须真实创建外部 SDK 连接，测试沿用该工程已有替代依赖。

## 4. 配置、补充声明和生成文件保留既有名称

```text
src/config/env.ts                         # 在现有环境来源增加已确认项
src/types/assets.d.ts                     # 增加所需资源声明
<既有源 Schema 文件>                      # 增加已确认字段
<既有生成位置>/schema.generated.ts        # 运行原生成器更新
src/app/<既有组装位置>/...                 # 如新项需要传给 HTTP，则更新必要字段接线
src/integrations/http/<既有契约位置>/...    # 仅在输入契约受影响时更新
```

以上均保留原路径角色，不统一重命名为 `constants.ts` 或 `types.ts`。

- **环境项：** 在 `config/env.ts` 的现有环境读取和转换机制中接入已确认项，沿用它的名称、类型、必选性和既定缺失处理。应用组装只向 HTTP 接入传递所需字段；HTTP 不反向读取启动代码，也不导入整份环境配置。题设未给环境项详情，因此不能虚构变量名、默认值或新的配置加载器。
- **资源声明：** 在 `types/assets.d.ts` 中增加明确模块模式及与实际加载结果匹配的具体类型；若工具链公开了准确类型，直接引用它。题设未给新增扩展名和加载器行为，因此不假定资源必然是字符串、数字或组件。不使用 `declare module '*'`、无类型模块声明或 `any` 消除错误。
- **生成文件：** 在既有生成器认可的源 Schema 中增加已确认字段，再使用既有生成命令重生成 `schema.generated.ts`。不手工编辑生成物，也不重写一份字段接口。消费者需要的生成类型经所属单元 `types.ts` 引用或再导出，再由小型公共入口按需公开；生成文件内部导出不等于公共 API 全部导出。

验证分别对应来源与接线：环境读取在受控输入下覆盖已确认项的解析、缺失处理及组装到 HTTP 的必要字段传递；资源声明通过真实导入使用处的类型检查和受影响目标的构建或资源加载验证，不以声明编译成功代替实际加载正确；生成链路运行原生成器和既有一致性检查，核对输出 diff、类型、运行时校验和需要的模型 Schema 都反映同一新增字段，并验证实际受影响消费者的必填/可选、编码解码及展示或请求转换行为。没有新增原生配置时，不因这些文件名默认要求全部设备验证。

## 消费者定位与证据边界

对公共类型、固定值、生成类型和公开入口的变化，在真实工程中先以 `rg` 或既有静态引用工具查询符号名、旧路径、新入口和重导出，核对生产方与调用链中的实际消费者；检查 TypeScript、ESLint 及已有导入/循环依赖约束。仅类型导入也要通过所属公开入口，不能用 `import type` 穿透私有状态或生成实现路径；不新增全局总 barrel。

随后检查所属契约已记录的非静态关系，包括适用的模型 Schema 生成链、宿主接线、H5 协议、Web 预览和跨仓使用方。关系存在才纳入对应验证；不能凭一次文本搜索或 Jest 相关测试选择宣称影响已完整覆盖。优先运行对应单元、生产方和实际受影响组合的测试；发现引用范围遗漏或语义变化再扩大。合并、发布仍按目标工程已有 CI 要求执行。

本次可确认的是上述文件归属、出口与验证设计；实际消费者名单、生成命令、环境项和资源类型尚未由题设提供，未虚构补齐，亦不声称相关测试、构建或外部运行已经通过。
