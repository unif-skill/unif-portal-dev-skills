# 本批方案

保留 `ensureDraft({ customerId }, deps)` 和 `capturePhoto(input, deps)`，无需拆分公共函数，也无需等待整个营销领域重新设计。题目已确认它们的职责、参数、结果和副作用，本批可以直接完成所属类型文件、公开出口与受影响导入的等价整理。

判断依据为本批 B 材料中 architecture-design 的「功能、场景与入口」「状态归属」「独立开发与验证」，以及 portal-development 的「文件规则」「依赖规则」「定向验证」。这些规则允许功能通过明确依赖和局部状态完成自身契约；已有公共语义不变的内部整理沿用已确认设计及有效测试。

## 职责与状态

- `ensureDraft` 是已有复合业务操作，语义明确包含“没有草稿时创建”。`find` 返回现有草稿时直接返回同一结果；只有严格等于 `null` 时调用一次 `create`，并直接返回新草稿。错误原样传播。把它拆成两个公共能力并让两个场景重复重建组合，会搬走已经确认且复用的公共语义，本批没有这种需要。`find`、`create` 可以继续作为内部 API 依赖；不新增公共出口、不重试、不补确认。该操作有创建副作用，不能把它当作只读查询用于其他消费者。
- `ensureDraft` 内的查询结果属于一次调用的局部快照。业务系统仍维护草稿记录的事实，Portal 场景仍维护用户编辑与提交交互状态；函数不隐式读取页面草稿或维护跨调用缓存。本批也不新增事务、并发唯一性或幂等保证。
- `capturePhoto` 完成一次拍摄、选用和产物交付。`session`、拍摄结果、`temporaryPath` 和转存结果均属于本次调用，适合留在函数内。打开会话、拍摄、转存、释放临时文件和关闭会话共同实现这一设备契约，不应让 UI 重建资源生命周期。
- 打开成功后通过外层 `finally` 关闭会话；选中后通过内层 `finally` 在 adopt 成功或失败时清除临时文件，然后关闭会话。取消不调用 adopt/remove，但必须 close；open 失败没有已返回会话可关闭，capture 失败没有已交付临时路径可删除，但仍 close。本题保证收尾成功，因而其他异常保持原对象传播。
- 能力交付成功前负责本次临时产物，持久 `uri` 交付后由调用方按既有用途管理。业务归属、上传和提交属于场景；本次不增加这些步骤。能力自身的照片选用与资源状态不等于业务提交状态。

“能力不能协调任何步骤、不能管理任何状态”不是本批规范的要求。跨独立业务目标的场景组合与一个操作内部必要的协调应按公共职责区分，不能按 SDK 调用次数划界。

## 最小文件与公开出口

在各自**现有所属位置**整理，不借本题推定新的顶层目录：

```text
<ensureDraft 所属位置>/ensureDraft/
  ensureDraft.ts
  types.ts
  index.ts
<capturePhoto 所属位置>/capturePhoto/
  capturePhoto.ts
  types.ts
  index.ts
```

若现有单元目录已经承载对应实现，直接使用已有目录与 `types.ts`，不再嵌套建立重复单元。实现文件保留函数和局部变量；所有显式类型移入所属 `types.ts`。本题没有需要独立维护的常量、样式、共享可变状态或 Schema，不创建空 `constants.ts`、`styles.ts`、`state.ts` 或校验框架，不把 session、SDK 资源或查询结果移出调用作用域。

公开入口具名导出既有函数以及调用方、依赖组装方所需的输入、结果和依赖类型。辅助结构可在所属 `types.ts` 导出以供单元内部使用，不批量导出到公共入口。示意：

```ts
// ensureDraft/index.ts
export { ensureDraft } from './ensureDraft';
export type { Draft, EnsureDraftInput, EnsureDraftDeps } from './types';

// capturePhoto/index.ts
export { capturePhoto } from './capturePhoto';
export type { CapturePhotoResult, CapturePhotoDeps } from './types';
```

实现使用 `import type` 引用所属类型。两个已知草稿场景继续消费同一 `ensureDraft` 公共入口。若物理文件调整影响既有导入，保持原公共路径为显式重导出，或在本批同步全部已知消费者；不创建横跨业务与设备的总 barrel。题目未提供真实文件路径，因此以上是可应用方案，不声称已完成真实导入迁移。

## 必要 TypeScript 类型

题目没有规定标识符的底层类型和拍摄 input 的字段。下面用类型参数保留由现有工程决定的类型，不增加参数、业务字段或输入转换；接入时可直接引用所属工程既有的公开类型。对象结构均由 interface 定义，联合由 type 组合。

```ts
// ensureDraft/types.ts
export interface EnsureDraftInput<CustomerId> {
  customerId: CustomerId;
}

export interface Draft<CustomerId, DraftId> {
  id: DraftId;
  customerId: CustomerId;
}

export interface DraftApi<CustomerId, DraftId> {
  find(input: EnsureDraftInput<CustomerId>):
    Promise<Draft<CustomerId, DraftId> | null>;
  create(input: EnsureDraftInput<CustomerId>):
    Promise<Draft<CustomerId, DraftId>>;
}

export interface EnsureDraftDeps<CustomerId, DraftId> {
  api: DraftApi<CustomerId, DraftId>;
}

// 实现签名，类型通过 import type 从 ./types 引用
export declare function ensureDraft<CustomerId, DraftId>(
  input: EnsureDraftInput<CustomerId>,
  deps: EnsureDraftDeps<CustomerId, DraftId>,
): Promise<Draft<CustomerId, DraftId>>;
```

```ts
// capturePhoto/types.ts
export interface SelectedPhoto {
  kind: 'selected';
  temporaryPath: string;
}

export interface CancelledPhoto {
  kind: 'cancelled';
}

export type SessionCaptureResult = SelectedPhoto | CancelledPhoto;

export interface AdoptedPhoto {
  uri: string;
}

export interface SuccessfulPhoto {
  kind: 'success';
  uri: string;
}

export type CapturePhotoResult = SuccessfulPhoto | CancelledPhoto;

export interface PhotoSession {
  capture(): Promise<SessionCaptureResult>;
  close(): Promise<void>;
}

export interface PhotoDevice<Input> {
  open(input: Input): Promise<PhotoSession>;
}

export interface PhotoFiles {
  adopt(temporaryPath: string): Promise<AdoptedPhoto>;
  remove(temporaryPath: string): Promise<void>;
}

export interface CapturePhotoDeps<Input> {
  device: PhotoDevice<Input>;
  files: PhotoFiles;
}

// 实现签名，类型通过 import type 从 ./types 引用
export declare function capturePhoto<Input>(
  input: Input,
  deps: CapturePhotoDeps<Input>,
): Promise<CapturePhotoResult>;
```

上例使用异步依赖签名表达 API/设备操作；实际工程若已有同步资源收尾类型，沿用该类型即可，运行实现的 `await` 同样接受同步返回。无需为未知错误添加新的结果分支或包装错误。本题未要求执行 Schema，类型不形成另一套运行期校验来源。

真实可执行函数位于同目录 `solution.mjs`，使用具名 ESM 导出，可由 Node.js 直接导入；不是固定返回或伪代码。

## 验证与本次交付边界

已执行：使用 Node.js 导入本批 `solution.mjs`，以 `node:assert/strict` 和替代外部依赖运行 9 个合成用例，输出 `PASS 9 synthetic behavior cases`，命令退出码为 0。

| 路径 | 已断言的结果与副作用 |
|---|---|
| 草稿存在 | 返回 find 的同一对象；参数正确；不 create |
| 草稿不存在 | find 后 create 各一次；参数正确；返回 create 的同一对象 |
| find 失败 | 原错误对象传播；不 create |
| create 失败 | 原错误对象传播；不重试 |
| 拍摄成功 | 原 input 传给 open；adopt 使用选中路径；返回持久 uri；调用顺序 open → capture → adopt → remove → close |
| 拍摄取消 | 返回 cancelled；仅 open → capture → close |
| open 失败 | 原错误对象传播；不调用后续方法 |
| capture 失败 | 原错误对象传播；close 一次；不 adopt/remove |
| adopt 失败 | 原错误对象传播；remove 后 close，均一次 |

本次实际写入仅有评测输出目录中的方案与函数文件，没有修改真实工程。对已授权真实工程整理的应用阶段，仍需按现有工具完成：

1. 核对并调整既有公共路径、两个草稿场景及实际照片消费者的导入和依赖组装；检查类型引用、私有深路径与循环依赖。
2. 运行现有 TypeScript 检查及本函数相关既有用例，复用正常、取消、失败和收尾断言。公共类型变化应覆盖实际生产方与消费者；不因文件归属就默认重跑整个营销领域。
3. 如果发现公共语义、原生适配、宿主或 H5 接线发生变化，再扩大到受影响的组合、接线、平台构建和设备验证；发布阶段按工程既定 required CI 执行。

这里没有执行 TypeScript 编译、真实工程测试、完整 CI、依赖安装、设备操作或真实 API 调用。9 个合成用例证明本批函数在替代依赖下的行为，不能证明真实工程接线、SDK 安装或设备产物生命周期已经生效。
