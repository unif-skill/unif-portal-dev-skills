# Schema、纯工具与应用文件

这是采用新 Portal 规则的合成工程。请给出以下文件变更后的最小文件组织、关键代码或导出，并说明实际需要的验证；所有外部库名称仅是题设。

1. `domains/marketing/orderInput/schema.ts` 已使用项目采用的 Zod 定义 `orderInputSchema = z.object({ customerId: z.string(), quantity: z.number() })`。运行时和模型 Schema 都由它产生。当前没有别的字段，本次仅让两个消费者能导入静态类型。有人准备在 `types.ts` 重写同字段的 `interface OrderInput`，也有人准备为所有单元新增 Zod。
2. 当前 `utils/trimLabel.ts` 只有 `export function trimLabel(value: string) { return value.trim(); }`。本批仅补输入样本，行为不变。对照另一独立批次：它增长为带显式 `TrimOptions` 对象参数和已有产品要求的固定长度上限 `MAX_LABEL_LENGTH = 40`，同时有一个只被本函数使用的私有截取辅助函数。分别给出文件组织；不要将这两个批次混为同一次实现。
3. `useLookup.ts` 中的 `const client = createClient()`、`const pending = new Map()` 与 `const value = props.query.trim()` 都是当前 hook 实例的运行期内容。`const MODE_LABELS = {name:'名称',code:'编号'}` 是所属查询单元的固定展示映射。分类建议按 `const` 关键字统一搬到 constants.ts，或者另建 variables.ts。请说明实际放置和生命周期；原有实例隔离已经满足，本次不引入持久化。
4. `config/env.ts` 已负责读取构建环境，应用组装把必要字段传给 HTTP 接入；`types/assets.d.ts` 已声明图片模块，`schema.generated.ts` 是既有生成器的输出。这次分别新增一个已确认环境项、一种资源声明和一个源 Schema 字段。是否应统一重命名为 constants.ts/types.ts？需要如何修改与验证？

跨单元只公开消费者需要的类型和函数。公共固定值、生成类型或公开入口变化时，说明如何找到并验证实际消费者；不要把宽泛 any、私有深路径 import type 或全局总 barrel 当作统一方案。
