拒绝把统一运行环境整体注入查询。`queryNearby` 的职责是按明确客户、位置和页号读取一页；是否调用、准备输入、复用结果和后续交互由调用入口或场景决定。“没有业务写入”不能作为扩展查询职责的依据。

采用指定的 `architecture-design` 中调用组合、交互确认和独立验证规则，以及 `portal-development` 的文件与类型规则。题目已经明确刷新与分页语义，无需额外增加公共状态、查询模式或协调框架。

| 行为 | 触发与输入准备 | 实际调用与结果 |
| --- | --- | --- |
| 明确刷新 | 刷新按钮触发；入口先取得客户 | `refreshNearby` 每次先等待 `location.read()`，再将该位置和本次客户传给 `queryNearby`，固定 `page: 1`；返回 `{ location, result }` |
| 已有位置和结果 | 展示由现有列表状态负责 | `previousLocation` 只兼容既定函数形状，不参与本次刷新决策；旧观测可用也必须重新定位 |
| 普通翻页 | 用户点击下一页；入口从当前已显示列表快照取得客户、位置和指定页 | 直接调用 `queryNearby` 一次；不读取实时客户、不定位、不循环读取 `nextPage` |
| 必要输入缺失 | 有 UI 的入口可以先等待客户选择；无 UI 调用方自行准备参数 | 直接调用公共查询而缺参时返回 `invalid-input`，不触碰任何依赖；不自动读取当前客户、草稿或缓存 |
| 等待选择 | 所属交互调用 `interaction.requestCustomer()`，选择完成后继续准备 | 等待期间不调用查询；示例以 `null` 表示取消，取消后入口停止本次刷新 |
| 后续选择与确认 | 已有业务交互在用户发起后续操作时处理 | 不属于这两个函数；不因查询结束或存在后续页而调用 `interaction.confirm()` |

`queryNearby` 实际仅需 `transport.query`。`refreshNearby` 是普通场景组合，需要定位依赖与查询的传输依赖；传给内部查询时仅保留 `transport`。组装代码仍可以持有完整运行环境，但应在调用处收窄依赖。`scene.currentCustomer`、`draft.read`、`cache.get`、定位和交互都不进入公共查询。已显示结果可以供入口展示；这不授权跳过明确刷新或这次有效查询。传输结果原样返回，传输异常原样传播；定位失败也向调用方传播，本次刷新不回退旧位置或继续查询。

必要 TypeScript 契约如下。本合成设计将客户标识定义为非空字符串；位置为两个有限数值，允许零坐标；页号在运行时验证为正整数。`number` 本身不能证明页号有效。TypeScript 调用方必须提供全部查询字段，运行时仍验证 JavaScript 等调用方的缺参。

```ts
interface Location {
  latitude: number;
  longitude: number;
}

interface QueryNearbyInput {
  customerId: string;
  location: Location;
  page: number;
}

interface QuerySuccess<TItem> {
  kind: 'success';
  items: TItem[];
  nextPage?: number;
}

interface InvalidInput {
  kind: 'invalid-input';
}

type QueryNearbyResult<TItem> = QuerySuccess<TItem> | InvalidInput;

interface QueryNearbyDeps<TItem> {
  transport: {
    query(input: QueryNearbyInput): Promise<QuerySuccess<TItem>>;
  };
}

interface RefreshNearbyInput {
  customerId: string;
  previousLocation?: Location;
}

interface RefreshNearbyDeps<TItem> extends QueryNearbyDeps<TItem> {
  location: {
    read(): Promise<Location>;
  };
}

interface RefreshNearbyResult<TItem> {
  location: Location;
  result: QueryNearbyResult<TItem>;
}

declare function queryNearby<TItem>(
  input: QueryNearbyInput,
  deps: QueryNearbyDeps<TItem>,
): Promise<QueryNearbyResult<TItem>>;

declare function refreshNearby<TItem>(
  input: RefreshNearbyInput,
  deps: RefreshNearbyDeps<TItem>,
): Promise<RefreshNearbyResult<TItem>>;
```

题目要求的真实实现位于同目录 `solution.mjs`，具名导出上述两个函数，不依赖 UI 或第三方包。若接入 TypeScript 工程，在现有所属单元中采用 `queryNearby.ts`、`refreshNearby.ts`、`types.ts` 和小型 `index.ts`；前两者分别承担查询能力与刷新组合，类型仅维护一份。校验辅助保持实现文件内的普通私有函数，不为这次题目增加常量、状态、Schema 框架或新目录体系；最终目录落点应按目标工程现状确认。本次仅生成题目指定的两个产物。

入口可以使用普通私有函数完成交接。以下为示例，`displayedList` 是已有列表状态，`refreshDeps` 由应用组装；选择函数返回客户标识或 `null`。页面既有的异步结果接收规则继续由页面负责。

```js
async function handleRefresh(customerId) {
  const selectedId = customerId ?? await interaction.requestCustomer();
  if (selectedId == null) return;
  const { location, result } = await refreshNearby(
    { customerId: selectedId, previousLocation: displayedList?.location },
    refreshDeps,
  );
  if (result.kind === 'success') {
    displayedList = { customerId: selectedId, location, result };
  }
  return result;
}

async function handleNextPage(page) {
  const list = displayedList;
  if (!list) return;
  const result = await queryNearby(
    { customerId: list.customerId, location: list.location, page },
    { transport: refreshDeps.transport },
  );
  if (result.kind === 'success') displayedList = { ...list, result };
  return result;
}
```

可验证的调用次序与反例：

- 刷新客户 A，已有位置 L0：`location.read → 返回 L1 → transport.query({ A, L1, page: 1 })`。`{ A, L0, page: 1 }`、直接显示缓存、先查询再定位均违反本次刷新语义；定位失败时不能用 L0 补救。
- 已显示客户 A、位置 L1 的列表，用户点击第 7 页：只有 `transport.query({ A, L1, page: 7 })`。即使运行环境的当前客户变为 B，也不能替换这次列表的客户。结果包含 `nextPage` 时不得自动继续读取。
- 缺少客户直接调用查询：立即得到 `invalid-input`，调用记录为空。自动取当前客户、打开选择交互或用草稿补参都改变了公共查询契约。
- 入口缺客户：`requestCustomer → 等待 → 选中客户 C → location.read → query(C, 新位置, 1)`。取消后不定位、不查询；返回列表后不执行确认。
- 只有 `transport` 的无 UI 调用方应当能够查询。额外要求 `scene`、`draft`、`cache`、`location` 或 `interaction` 就扩大了不必要的依赖面。

已执行验证：`node --check solution.mjs` 通过；Node.js 直接导入真实两个导出函数，使用 `node:assert/strict` 和替代依赖执行 8 组行为检查，全部通过。其中包括 19 个无效输入且零依赖访问、等待定位完成后以新位置查第一页、指定第 7 页只读取一次并原样返回结果、零坐标与空成功列表、查询与刷新按同一异常对象拒绝、定位失败时不查询、普通入口等待客户选择和取消行为。有效查询通过依赖代理断言只访问 `transport`；后续页未预取，确认未调用。没有用替代函数冒充被测查询或刷新实现。

拟执行的工程验证：接入时对真实刷新按钮、翻页入口和无 UI 消费者做定向调用与类型检查，确认列表快照来自同一次查询，交互选择结果能满足必填参数，宿主已注入定位与传输适配。若公共参数、返回结果或定位适配发生变化，再扩大到实际受影响消费者及设备链路。本次没有运行 TypeScript 编译、真实工程测试、CI、网络联调或真机检查；这些不属于当前已有证据。
