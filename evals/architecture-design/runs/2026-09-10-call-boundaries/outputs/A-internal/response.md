# 本批结论

保留 `ensureDraft({ customerId }, deps)` 和 `capturePhoto(input, deps)` 两个公共函数及现有语义。本批可以直接完成所属 `types.ts`、实现文件和小型公开出口的整理，同步两个草稿消费者及拍照实际消费者的导入，复用既有行为测试。不需要先重新设计整个营销领域。

题目已经确认 `ensureDraft` 是“查询同一客户草稿，明确不存在时创建”的复合业务操作。`find`、`create` 是它内部接入的 API 步骤，创建副作用已经在公共语义中明确。没有依据把它拆成两个新的公共能力，再让两个场景复制同一段协调逻辑；也不增加重试或确认。查询返回草稿时直接返回该对象；仅 `null` 才创建，并直接返回创建结果。任何查询或创建异常保持原值传播。

`capturePhoto` 负责完整的一次拍摄、选用、产物交付与本次临时资源收尾。`open → capture → adopt` 是完成此能力的内部步骤，`remove`、`close` 是同一能力的生命周期责任，可以使用注入的设备与文件依赖。能力可协调自身契约必需的步骤，也可持有本次调用的局部状态；“只允许一次 SDK 调用”“不能管理状态”都不成立。UI 调用此公共函数、展示结果，收到成功后由接收方管理持久照片；后续上传和业务提交仍由实际场景负责。

拍摄会话、选用结果和临时路径留在本次函数调用内，不搬入 `constants.ts`、全局 store 或公共状态对象。选用前或取消时没有待清理的已知临时路径；选中后即使转存失败也清理该路径；只要成功打开会话，就关闭该会话。草稿查询结果和创建回执仍来自业务系统，函数中的局部引用不另建一份客户端权威草稿。

以上判断采用题目给定契约，并对应 `architecture-design` 的 `composition.md`、`state.md`、`scope.md`、`verification.md`，以及 `portal-development` 的 `file-rules.md`、`dependencies.md`、`testing.md`：公共职责由契约与消费者确定，内部辅助保留普通代码，等价整理按本批影响范围验收。

# 最小文件和导出方案

沿用两个操作当前所属单元，不猜测合成工程未给出的顶层目录。如果当前还是独立单文件，则以操作名建立对应单元目录；如果已有单元目录，则直接使用其现有角色文件。

| 单元 | 必要文件 | 作用 |
|---|---|---|
| 草稿操作所属单元 | `ensureDraft.ts`、`types.ts`、`index.ts` | 实现、该单元显式类型、具名公开出口 |
| 拍照能力所属单元 | `capturePhoto.ts`、`types.ts`、`index.ts` | 实现、该单元显式类型、具名公开出口 |

不新增没有内容的 `constants.ts`、`styles.ts`、`state.ts`、Schema 或辅助类。`session`、`result`、`temporaryPath` 即使用 `const` 声明也属于本次调用。没有独立消费者的底层步骤不新增公共函数。已有公开导入路径优先保持；物理移动确实影响路径时，在原公共入口具名转导出并同步所需内部引用，不要求消费者穿透实现文件。

草稿单元的 `index.ts`：

```ts
export { ensureDraft } from './ensureDraft';
export type { Draft, EnsureDraftInput, EnsureDraftDeps } from './types';
```

拍照单元的 `index.ts`：

```ts
export { capturePhoto } from './capturePhoto';
export type { CapturePhotoDeps, CapturePhotoResult } from './types';
```

不使用 `export *` 汇出所有内部步骤或整个领域。依赖结构中的会话等接口可以从所属 `types.ts` 导出供本单元使用，不自动成为 `index.ts` 的额外具名出口。应用组装按原方式注入实际依赖，运行期资源不因整理文件变成跨调用共享实例。

# 必要 TypeScript 类型

以下用泛型保留题目未指定的草稿标识类型和拍照输入形状；落入真实工程时沿用已存在的准确类型，不改字段、不转换标识，也不虚构相机配置项。`Awaitable` 只表达此实现可等待同步值或异步结果，是各单元内部的基本辅助类型，无需新建公共工具模块。

草稿单元 `types.ts`：

```ts
type Awaitable<T> = T | PromiseLike<T>;

export interface EnsureDraftInput<CustomerId> {
  customerId: CustomerId;
}

export interface Draft<CustomerId, DraftId> {
  id: DraftId;
  customerId: CustomerId;
}

export interface DraftApi<CustomerId, DraftId> {
  find(input: EnsureDraftInput<CustomerId>):
    Awaitable<Draft<CustomerId, DraftId> | null>;
  create(input: EnsureDraftInput<CustomerId>):
    Awaitable<Draft<CustomerId, DraftId>>;
}

export interface EnsureDraftDeps<CustomerId, DraftId> {
  api: DraftApi<CustomerId, DraftId>;
}
```

实现文件引用这些类型，保持签名：

```ts
export async function ensureDraft<CustomerId, DraftId>(
  { customerId }: EnsureDraftInput<CustomerId>,
  deps: EnsureDraftDeps<CustomerId, DraftId>,
): Promise<Draft<CustomerId, DraftId>>;
```

拍照单元 `types.ts`：

```ts
type Awaitable<T> = T | PromiseLike<T>;

export interface SelectedPhoto {
  kind: 'selected';
  temporaryPath: string;
}

export interface CancelledPhoto {
  kind: 'cancelled';
}

export type CaptureSelection = SelectedPhoto | CancelledPhoto;

export interface PersistentPhoto {
  uri: string;
}

export interface CapturePhotoSuccess {
  kind: 'success';
  uri: string;
}

export type CapturePhotoResult = CapturePhotoSuccess | CancelledPhoto;

export interface CaptureSession {
  capture(): Awaitable<CaptureSelection>;
  close(): Awaitable<void>;
}

export interface PhotoDevice<Input> {
  open(input: Input): Awaitable<CaptureSession>;
}

export interface PhotoFiles {
  adopt(temporaryPath: string): Awaitable<PersistentPhoto>;
  remove(temporaryPath: string): Awaitable<void>;
}

export interface CapturePhotoDeps<Input> {
  device: PhotoDevice<Input>;
  files: PhotoFiles;
}
```

实现文件引用这些类型，保持签名：

```ts
export async function capturePhoto<Input>(
  input: Input,
  deps: CapturePhotoDeps<Input>,
): Promise<CapturePhotoResult>;
```

这两段签名是类型方案，不是函数体。可直接由 Node.js 导入的真实函数体已保存在同目录 `solution.mjs`，分别具名导出 `ensureDraft` 和 `capturePhoto`。异常仍是拒绝结果，未增加包装错误或失败联合分支。拍照采用嵌套 `try/finally`，确保先等待临时文件清理，再关闭会话；题目保证两项收尾成功，因此不会覆盖原操作异常。

# 验证与交付边界

已执行：通过 Node.js 导入此次 `solution.mjs`，使用内置 `node:assert/strict` 和外部依赖替身，验证 10 个合成行为用例，输出 `PASS 10 synthetic behavioral cases`。

| 合成用例 | 已断言的结果与副作用 |
|---|---|
| 草稿存在 | 只查询一次，返回同一草稿对象，不创建 |
| 草稿明确不存在 | 查询一次后创建一次，传入同一客户参数，返回创建对象 |
| 查询失败 | 原异常对象传播，不创建 |
| 创建失败 | 原异常对象传播，不重试 |
| 选中照片 | 原输入传给 open；`open → capture → adopt → remove → close` 各一次，返回持久 URI |
| 取消拍照 | 返回 cancelled；关闭会话，不转存、不删文件 |
| 打开失败 | 原异常对象传播，无 capture、adopt、remove 或 close |
| 拍摄失败 | 原异常对象传播，关闭已打开会话，无 adopt、remove |
| 转存失败 | 原异常对象传播，仍清理所选临时路径并关闭会话 |
| 两次拍照交错执行 | 一次转存挂起时另一调用可独立完成；各自清理自己的临时路径、关闭自己的会话，收尾不抢跑 |

真实工程中的本批拟执行验证：定位既有公开出口、直接引用与两个草稿场景消费者；类型抽取和导入调整后运行工程已有类型检查与导入约束，复用两个公共函数、相关适配和实际受影响消费者的既有测试。保留针对返回值、调用次数、顺序、取消和失败副作用的断言。若存在 H5 或宿主接线消费者，按真实关系补查；未提供工程证据时不宣称存在这些消费者或已覆盖。

本次仅写出评测输出目录中的方案和运行实现，没有修改真实工程。TypeScript 方案未执行真实工程编译，既有工程测试、CI、依赖接线和设备行为均未在本次执行。合成测试只证明所交付函数在给定依赖契约下的代码行为；没有安装、网络调用或设备操作。实际合并时仍按工程 required CI 验证；如果后续变更了原生 SDK、平台适配或产物生命周期契约，再扩大到相关构建和真机验证。现有等价文件整理不以整个营销领域重设计或整域测试作为前置条件。
