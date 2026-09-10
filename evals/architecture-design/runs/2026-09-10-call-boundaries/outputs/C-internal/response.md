# 本批交付结论

保留 `ensureDraft({ customerId }, deps)` 和 `capturePhoto(input, deps)` 两个公共操作及现有语义。本批可以直接完成类型提取、角色文件整理、具名出口和受影响导入的同步；题目中的既有契约已足够，不需要重新设计整个营销领域。

把查询和创建下放给两个场景，会让场景重复实现已经确认的“存在则返回，仅明确不存在才创建”操作。`ensureDraft` 是具有创建副作用的复合业务操作，不是纯查询；调用方按已有场景规则决定调用和准备 `customerId`，函数内部负责完成该操作。它只读取显式输入和 `deps.api` 的实际返回，只有 `null` 才创建，直接返回草稿，异常原样传播。已有两个场景继续调用同一出口，沿用已确认的调用与确认责任。

拍摄会话、照片选用、转为持久产物和本次临时文件清理，都属于 `capturePhoto` 已确认的生命周期。“能力只能调用一次 SDK、不能管理任何状态”的拆分没有必要，会把资源管理泄漏给 UI。入口准备并传入 `input`，设备能力完成拍摄并交付结果；后续业务归属、上传和提交仍由使用场景安排。

依据为题目既有契约，以及本次读取的 `architecture-design` 中功能内部状态、设备产物交付和等价内部调整规则，`portal-development` 中角色文件、小型公开出口和定向验证规则。

## 最小文件与出口

沿用既有业务和设备单元位置；下面的 `…` 表示所属目录，不新建顶层架构。若既有目录已能承载这些文件，直接在其中整理。

```text
…/ensureDraft/
  ensureDraft.ts
  types.ts
  index.ts
…/capturePhoto/
  capturePhoto.ts
  types.ts
  index.ts
```

实现放同名文件；显式接口和联合类型移到各自 `types.ts`，实现使用 `import type`。沿用原来的可用公共导入路径，必要时让原入口转导出同一实现，并同步实际受影响的两个场景及设备消费者导入。测试继续复用现有位置和用例。

公共出口只提供这两个操作各自的函数、输入/结果和注入依赖类型，不导出内部步骤。无须把 `find`、`create`、`open`、`capture`、`adopt`、`remove`、`close` 包装成新增公共操作。对象结构使用 `interface`；联合类型由已命名接口组成。

```ts
// ensureDraft/types.ts
export interface EnsureDraftInput<CustomerId> {
  customerId: CustomerId;
}

export interface Draft<CustomerId, DraftId> {
  id: DraftId;
  customerId: CustomerId;
}

export interface EnsureDraftApi<CustomerId, DraftId> {
  find(input: EnsureDraftInput<CustomerId>): Promise<Draft<CustomerId, DraftId> | null>;
  create(input: EnsureDraftInput<CustomerId>): Promise<Draft<CustomerId, DraftId>>;
}

export interface EnsureDraftDeps<CustomerId, DraftId> {
  api: EnsureDraftApi<CustomerId, DraftId>;
}

// ensureDraft/index.ts
export { ensureDraft } from './ensureDraft';
export type { EnsureDraftInput, Draft, EnsureDraftDeps } from './types';

// ensureDraft.ts 的函数签名
// async function ensureDraft<CustomerId, DraftId>(
//   { customerId }: EnsureDraftInput<CustomerId>,
//   deps: EnsureDraftDeps<CustomerId, DraftId>,
// ): Promise<Draft<CustomerId, DraftId>>
```

标识符使用泛型承接已有类型，避免题目未指定其底层类型时擅自改成某一种标识格式。实际工程已有标识符定义时直接引用，不增加第二套字段源。

```ts
// capturePhoto/types.ts
export interface SelectedCapture {
  kind: 'selected';
  temporaryPath: string;
}

export interface CancelledCapture {
  kind: 'cancelled';
}

export type SessionCaptureResult = SelectedCapture | CancelledCapture;

export interface AdoptedPhoto {
  uri: string;
}

export interface PhotoSuccess {
  kind: 'success';
  uri: string;
}

export type CapturePhotoResult = PhotoSuccess | CancelledCapture;

export interface CaptureSession {
  capture(): Promise<SessionCaptureResult>;
  close(): void | Promise<void>;
}

export interface CaptureDevice<Input> {
  open(input: Input): Promise<CaptureSession>;
}

export interface CaptureFiles {
  adopt(temporaryPath: string): Promise<AdoptedPhoto>;
  remove(temporaryPath: string): void | Promise<void>;
}

export interface CapturePhotoDeps<Input> {
  device: CaptureDevice<Input>;
  files: CaptureFiles;
}

// capturePhoto/index.ts
export { capturePhoto } from './capturePhoto';
export type { CapturePhotoResult, CapturePhotoDeps } from './types';

// capturePhoto.ts 的函数签名
// async function capturePhoto<Input>(
//   input: Input,
//   deps: CapturePhotoDeps<Input>,
// ): Promise<CapturePhotoResult>
```

`Input` 保留题目未展开的既有设备输入并原样传入 `open`，不增添拍摄选项。接入真实工程时优先沿用已有 SDK/适配契约类型；上面是合成契约的必要结构。`CaptureSession` 等类型可以供单元内部引用，但无需全部进入公共 `index.ts`。

## 状态与收尾

`draft`、`session`、拍摄结果、临时路径和转存结果都是本次调用的局部值，留在实现函数内；这里没有实际需要新增的跨调用状态。使用 `const` 不意味着应移动到 `constants.ts`，也不创建空的 `constants.ts`、`state.ts` 或 `variables.ts`。

`capturePhoto` 的外层 `try/finally` 在成功打开会话后开始，确保捕获、取消或转存失败时关闭会话。选中后的内层 `try/finally` 包围 `adopt`，确保转存成功或失败都先删除本次临时文件，再由外层关闭会话。取消时没有临时路径，不转存或删除；打开失败时没有已打开会话可关闭。清理方法按题目保证成功，因此无需改写异常或引入补偿协议。成功交付的持久 `uri` 由接收方按场景契约管理。

## 验证范围与证据

已保存可由 Node.js 直接导入的真实实现 `solution.mjs`，导出 `ensureDraft`、`capturePhoto`。已用 Node.js 内置 `assert` 实际导入该文件，替换 API、设备和文件边界，运行并通过 9 个合成行为检查：

| 操作 | 已检查路径与断言 |
|---|---|
| ensureDraft | 已有草稿：返回同一对象，仅调用 find |
| ensureDraft | find 返回 null：按同一 customerId 创建一次，返回 create 的同一对象 |
| ensureDraft | find 失败：同一错误原样拒绝，create 未调用 |
| ensureDraft | create 失败：同一错误原样拒绝，无重试 |
| capturePhoto | 成功：输入对象原样交给 open，顺序为 open → capture → adopt → remove → close，返回持久 uri |
| capturePhoto | 取消：仅 open → capture → close，返回 cancelled |
| capturePhoto | open 失败：同一错误原样拒绝，无捕获、转存、删除或关闭调用 |
| capturePhoto | capture 失败：同一错误原样拒绝，只补 close |
| capturePhoto | adopt 失败：同一错误原样拒绝，仍 remove → close |

各路径通过完整调用记录断言参数、顺序及次数，清理依赖的替代实现没有调用真实文件或设备。命令结果为 `9 synthetic behavior checks passed`。

真实工程的拟执行验证是：按静态引用核对原公开入口及实际消费者，运行现有 TypeScript/导入约束检查，复用两个操作及受影响场景、适配、入口接线的既有测试；存在 H5 或宿主等非静态消费者时核对对应引用。发现契约、共享状态、平台适配或实际行为变化才按影响扩大范围；文件整理本身不要求重跑整个营销领域。合并或发布阶段仍遵循目标工程实际 required CI。

本次实际只写入评测输出目录。上述 TypeScript 文件方案未在真实工程落地或编译，未运行真实工程测试、CI、构建、安装或真机验证，也未验证业务 API 或真实文件生命周期；合成代码通过不构成这些环节已经生效的证据。
