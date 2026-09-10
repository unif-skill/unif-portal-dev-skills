# Schema、纯工具与应用文件的最小修改方案

已使用题设指定的 `portal-development` 技能，依据其开发规则第 2—5 节、工程组织第 3—4、6 节判断文件角色和验证范围。本回答是书面修改方案；只读取题设与该技能目录，没有目标工程源码、真实配置或测试执行结果。下列 `src/` 是工程源码根的表示，现有公开入口优先沿用。

## 1. 订单输入：从已有 Schema 派生静态类型

保留 Zod Schema 为唯一字段源。本次只增加静态类型出口，不改两个现有字段、运行时校验和模型 Schema 的生成方式，也不为其他单元新增 Zod。

```text
src/domains/marketing/orderInput/
├── schema.ts       # 既有可执行契约
├── types.ts        # 新增必要推导类型
└── index.ts        # 沿用或补充本单元的小型公开入口
```

`schema.ts` 保留题设实现以及既有 Zod 导入：

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

这里的 `zod` 表示题设已采用的依赖；若工程经明确的公共文件引入 Zod，沿用该入口。不得新装另一版本。本次 Schema 没有变换，输入输出静态形状相同，不需要再增加 `OrderInputRaw` 等类型。

本单元 `index.ts` 增加以下具名类型导出，保留原有实际需要的导出：

```ts
export type { OrderInput } from './types';
```

两个消费者都从该单元公开入口取得类型：

```ts
import type { OrderInput } from '@/domains/marketing/orderInput';
```

不手写重复字段的 `interface OrderInput`。对象手写结构使用 interface 的一般规则不能破坏 Schema 同源要求。也不因新增此类型而公开 Schema、私有内部类型或所有领域类型；原有运行时消费者的合法入口照常维护。

验证：类型检查必须包括两个消费者，检查公开类型导出和路径解析；运行已有订单输入 Schema 的相关测试，确认有效输入和字段类型错误仍按原契约处理。模型 Schema 若有既有生成/一致性检查，运行该定向检查以确认静态导出不改变输出。没有字段变化，无需新增模型调用、全领域行为测试或真实业务请求。

## 2. trimLabel：两个批次分别处理

### 批次 A：仅补输入样本，行为不变

```text
src/utils/trimLabel.ts
__tests__/utils/trimLabel.test.ts
```

实现保持原样：

```ts
export function trimLabel(value: string) {
  return value.trim();
}
```

没有显式配套结构或命名固定值，不建 `trimLabel/` 目录，不建空 `types.ts`、`constants.ts` 或工具总 barrel。实现文件就是明确的公开文件。

输入样本放在对应现有测试中，只有此测试使用时不移到全局 fixture。可补充下列断言数据，适配工程已有测试框架：

```ts
const samples = [
  ['', ''],
  ['   ', ''],
  ['  名称  ', '名称'],
  ['\t名称\n', '名称'],
  [' 名 称 ', '名 称'],
  ['  abc  ', 'abc'],
];
```

长字符串也应保留完整内容；例如 41 个 `a` 的输出仍为 41 个 `a`，本批没有 40 字限制。这里的测试局部样本属于测试数据，不需要新增生产常量。

验证：运行 `trimLabel` 的定向输入输出测试及已有配置要求的相关静态检查。实现、位置和出口未改变，不需要为此默认重跑所有工具或领域测试。

### 独立批次 B：增加显式 TrimOptions 与既定长度上限

此批采用已有产品要求，不能与批次 A 合并成一次行为调整。

```text
src/utils/trimLabel/
├── trimLabel.ts
├── types.ts
├── constants.ts
└── index.ts
__tests__/utils/trimLabel.test.ts
```

`types.ts` 用 `export interface TrimOptions` 声明已确认的对象参数字段；题设未提供字段，不在本回答中发明 `maxLength`、截断开关、默认值或宽泛索引签名。实现文件导入该接口，函数签名为 `trimLabel(value: string, options: TrimOptions)`；是否支持省略 options 只能沿已确认契约，不能自行新增默认参数。

`constants.ts`：

```ts
export const MAX_LABEL_LENGTH = 40;
```

`index.ts`：

```ts
export { trimLabel } from './trimLabel';
export type { TrimOptions } from './types';
```

主实现从 `./types` 和 `./constants` 相对导入依赖。只被本函数使用的截取辅助函数留在 `trimLabel.ts`，不导出、不再建辅助目录、不移动到全局 `utils`。长度计算、先 trim 还是先截取，以及 options 的作用必须沿已有产品要求；题设没给出 Unicode 长度单位与选项字段，因此这里提供可确定的组织和出口，不伪造完整业务算法。

`MAX_LABEL_LENGTH` 默认仅供单元内部实现使用。若已查实某个消费者需要展示同一限额，则在本单元公开入口具名导出该常量，让该消费者引用唯一值；不能在消费者重复写 40，也不能深路径读取 `constants.ts`。没有该使用方时不额外公开。

验证：搜索现有 `trimLabel` 导入及调用，核对文件改为目录后编译器、测试运行器、构建器的实际解析；移除旧实现文件，避免新旧同名实现并存。同步需要 options 的实际调用方。运行工具的选项行为、空白与空值字符串、39/40/41 长度边界测试，并依据已确认长度单位检查对应字符样本。因返回内容可能截断，继续验证实际依赖完整标签或限额的消费者用例，不能仅凭类型检查宣称行为兼容。公开常量时还要验证其展示与计算语义一致。

## 3. useLookup：依据生命周期分类

```text
src/<现有所属查询单元>/
├── useLookup.ts
└── constants.ts
```

`constants.ts`：

```ts
export const MODE_LABELS = {
  name: '名称',
  code: '编号',
};
```

`useLookup.ts` 从 `./constants` 导入映射。该导出只服务单元内部跨文件使用，不自动进入公共 index.ts。若确有其他单元的展示消费者，再通过查询单元公开入口具名导出。

以下内容继续处于原 hook 实例的运行期作用域与既有初始化机制中：

- `client = createClient()` 是实例资源；保持原有创建、使用和清理责任。
- `pending = new Map()` 是运行期可变容器；保持原实例的读写者和生命周期。
- `value = props.query.trim()` 是当前输入的计算结果；仍在读取当前 props 的逻辑中计算。

不能把这些值放到模块顶层、`constants.ts` 或统一的 `variables.ts`。题设已经说明实例隔离满足，本次不重写为新的 ref/store，不额外引入共享状态、缓存、持久化或新的资源释放调用。仅凭这三行片段也不能推断现有初始化机制有缺陷。

验证：检查仅固定映射发生移动，现有初始化位置及实例隔离保持；运行该 hook 现有的输入更新、映射展示与生命周期相关用例。若此次移动涉及公开入口，补查实际消费者。实例隔离测试如已存在应继续通过；无需只因看到 `Map` 就设计持久化或真实连接 SDK。

## 4. 配置、声明与生成文件：保留各自用途和工具命名

```text
src/config/env.ts
src/app/<既有组装文件>
src/integrations/http/<实际受影响的接入文件>
src/types/assets.d.ts
<既有 Schema 源文件>
<既有位置>/schema.generated.ts
```

这些是现有路径角色示意，不要求建立新目录。三个变更分别沿其唯一来源维护，不统一改名为 `constants.ts` 或 `types.ts`。

| 对象 | 最小修改 | 定向验证 |
|---|---|---|
| `config/env.ts` | 增加已确认环境项的读取及工程已采用的解析/校验；应用组装向真正需要它的依赖传必要字段。若 HTTP 使用此项，同步现有接入参数契约与调用；不让下层读取整份环境配置 | 对该项的有效值、缺失或非法值按确认契约检查；核对构建环境注入与组装到 HTTP 的参数传递，运行受影响配置/接入测试 |
| `types/assets.d.ts` | 追加指定资源扩展名的模块声明，按实际加载器公开的值类型和导出方式描述 | 确认 tsconfig 包含声明文件；对真实资源导入消费者类型检查。核对现有加载器能处理该资源及相关打包配置；声明通过不代表资源可加载 |
| `schema.generated.ts` | 找到生成器的真正源 Schema，在源中加确认字段，执行原有生成器；保留生成文件名，检查产物 diff | 检查源与输出一致及现有生成一致性检查；类型检查生成类型消费者，运行受影响校验、序列化、映射与模型 Schema 测试，字段有协议语义时核对其现有契约 |

环境项名称、资源扩展名和导出类型、源字段定义都未在题设中展开，因此不虚构具体值或声明。资源声明不得使用 `declare module '*'` 或 `any` 掩盖类型缺口。生成类型对外公开时，按生成器现有类型名由所属单元的小型入口 `export type { ... }`，必要时由单元 `types.ts` 转出，不手写相同字段。模型与运行时契约继续从真实源生成，不能直接编辑生成文件作为最终修改。

## 5. 实际消费者和验证证据

在真实实施时，先用 `rg` 或工程静态引用工具查找符号及旧、新导入路径，包括 `OrderInput`、`orderInputSchema`、`trimLabel`、`MAX_LABEL_LENGTH`、`MODE_LABELS`，以及实际环境项、资源导入和生成类型名称。沿所属公开入口逐个确认直接消费者与重新导出者，再定位对应测试和应用组装。测试范围由该实际依赖关系决定；`import type` 仍遵守单元边界，不能作为读取私有深路径的理由。

静态引用之外，若此次字段或入口确实被 H5 协议、宿主注册、Web 预览或跨仓契约使用，还需按既有设计补齐这些消费者的检查。没有影响证据不扩大到全部能力、全部平台或整个营销领域。类型检查、已有导入规则及生成检查验证静态契约；码值、默认值、长度单位和序列化等语义要有对应行为断言。

本次实际完成的是限定资料阅读与书面文件组织、代码出口和验证设计，未修改合成工程、未执行其类型检查、测试、生成器或构建，也未访问 SDK、模型或业务系统。上述验证是落地时需要执行的范围，不能记录成已通过；技能规则本身也不证明目标工程已配置这些检查。
