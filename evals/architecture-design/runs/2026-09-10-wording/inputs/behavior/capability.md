# 设备与领域适配的定向修改

本题事实与接口仅用于合成工程。依据提供的 Portal 规则，给出两个独立改动的最小文件组织、关键代码和各自验证范围。保留已有公开名称；不安装依赖、不执行真实设备或业务请求。

## A. 设备能力

`capabilities/imagePicker/pickImage.ts` 暴露 `pickImage`，实际消费者为照片选择场景、头像选择以及 H5 图片选择桥。SDK 的本题契约：`PickerSdk.pick({limit, signal})` 返回选中文件 URI 数组；应用 bootstrap 提供 SDK 实例。本次只整理代码，不改变原有取消与结果语义：

```ts
interface PickInput { limit?: number; }
interface PickerSdk { pick(input: { limit: number; signal: AbortSignal }): Promise<string[]>; }
const DEFAULT_LIMIT = 1;
export async function pickImage(input: PickInput, sdk: PickerSdk) {
  const controller = new AbortController();
  const chosen = new Map<string, number>();
  const limit = input.limit ?? DEFAULT_LIMIT;
  const files = await sdk.pick({ limit, signal: controller.signal });
  files.forEach((uri, index) => chosen.set(uri, index));
  return Array.from(chosen.keys());
}
```

整理建议把全部 `const` 搬到 `constants.ts`，把 SDK 实例放全局 `config/sdk.ts`，能力通过 `app/bootstrap` 反向读取它；另给 Web 实现直接返回“选择成功”。公开默认数量的值可能在后续需求中改变，但本批没有该变更。原生宿主与 Web 支持范围未改变。

## B. 领域适配

已有 `domains/marketing/reasons` 单元的 `readReasons` 只读取原因选项，唯一消费者为完成场景的原因选择交互；保存原因与最终完成由该场景协调。接口确定数值 `code: 200` 为成功，字符串码不是已确认成功码。原始响应从 `{code:200,data:[{id,label}]}` 改为 `{code:200,data:[{id,name}]}`，功能结果仍给出相同语义的可选显示字段。返回数组可能含 `{id:'R1'}` 和 `null`；后续保存要求用户实际选择的真实原因标识。本次不改公共 HTTP、认证和取消协议。

有人建议把原始 DTO 和全部码表移到全局 `types/` 与 `config/`，每个页面自行映射，在缺少名称时默认选第一个原因，并在读取函数中直接保存。请给出本批适配组织和关键结果处理；指出类型检查之外需要验证的具体行为，以及哪些未来变化才应扩大到 H5、宿主或其他能力。
