不采纳把统一运行环境全部传给查询的提议。查询没有业务写入，不代表可以自行改变请求次数、条件、顺序和结果范围。这里的公共能力是“按客户、位置和页号读取一页”；重新定位、等待选择、翻页和后续确认各有明确触发者。

| 行为 | 触发与输入准备 | 实际调用 |
|---|---|---|
| 明确刷新 | 刷新入口提供本次客户，调用 `refreshNearby` | 每次先 `location.read()`，完成后以新位置调用 `queryNearby`，固定第一页 |
| 客户未选 | 交互协调代码调用 `interaction.requestCustomer()` 并等待；取得客户后才发起刷新 | 等待期间不查询、不定位；未取得客户则停留在交互 |
| 无 UI 调用 | 调用方自行准备必要条件 | `queryNearby` 缺参返回 `invalid-input`，不弹选择、不读取场景或草稿 |
| 普通翻页 | 下一页按钮传入指定页；调用方保存并提供当前已显示列表对应的客户和位置 | 直接调用一次 `queryNearby`；不重新定位、不切换成其他当前客户 |
| 后续业务选择与确认 | 由已有交互在对应业务操作中处理 | 查询完成不自动确认，也不驱动后续业务步骤 |

`previousLocation` 保留在既定刷新调用形式中，但不参与是否定位的判断，也不是定位失败的回退值。`nextPage` 只是返回数据，是否读取该页由下一次用户动作决定。缓存命中不能跳过这次明确刷新；当前契约没有在查询内部返回缓存或自动加载全部页的授权。

`queryNearby` 的唯一外部依赖是 `transport.query`。`refreshNearby` 是普通组合函数，依赖位置读取和查询传输，内部显式把传输交给查询。`scene.currentCustomer()`、`draft.read()`、`cache.get()` 和两个交互接口都不属于查询依赖。即使调用方传入额外属性，实现也不访问它们。

必要 TypeScript 契约如下。客户标识采用非空字符串，坐标采用有限数值，页号采用正整数；运行时做相同的必要输入检查，零坐标有效，不额外引入业务准入规则。有效请求沿用传输返回对象，保留条目、顺序和可选 `nextPage`，传输异常原样抛出。

```ts
export interface NearbyLocation {
  latitude: number;
  longitude: number;
}

export interface QueryNearbyInput {
  customerId: string;
  location: NearbyLocation;
  page: number;
}

export interface InvalidInputResult {
  kind: 'invalid-input';
}

export interface NearbySuccess<T> {
  kind: 'success';
  items: T[];
  nextPage?: number;
}

export type QueryNearbyResult<T> = NearbySuccess<T> | InvalidInputResult;

export interface NearbyTransport<T> {
  query(input: QueryNearbyInput): Promise<NearbySuccess<T>>;
}

export interface QueryNearbyDeps<T> {
  transport: NearbyTransport<T>;
}

export interface LocationReader {
  read(): Promise<NearbyLocation>;
}

export interface RefreshNearbyInput {
  customerId: string;
  previousLocation?: NearbyLocation;
}

export interface RefreshNearbyDeps<T> extends QueryNearbyDeps<T> {
  location: LocationReader;
}

export interface RefreshNearbyResult<T> {
  location: NearbyLocation;
  result: QueryNearbyResult<T>;
}

export declare function queryNearby<T>(
  input: QueryNearbyInput,
  deps: QueryNearbyDeps<T>,
): Promise<QueryNearbyResult<T>>;

export declare function refreshNearby<T>(
  input: RefreshNearbyInput,
  deps: RefreshNearbyDeps<T>,
): Promise<RefreshNearbyResult<T>>;
```

TypeScript 必填字段约束正常调用者，JavaScript 边界的缺参仍由真实实现返回 `invalid-input`。交互必须先解决未选客户；若直接错误调用刷新且没有客户，实现依然执行定位，随后由查询返回缺参结果，不暗中选择客户。定位失败直接向调用方传播，查询不会继续。

下面是交互侧普通私有函数示意；公共查询不承担等待状态。返回列表上下文的调用方负责接收并展示此次结果，翻页使用该上下文。后续业务确认继续使用已有业务操作交互。

```js
async function handleRefresh(customerId, previousLocation, deps) {
  const selectedCustomerId =
    customerId || await deps.interaction.requestCustomer();
  if (!selectedCustomerId) return;

  const refreshed = await refreshNearby(
    { customerId: selectedCustomerId, previousLocation },
    { location: deps.location, transport: deps.transport },
  );
  return { customerId: selectedCustomerId, ...refreshed };
}

async function handleNextPage(displayedList, requestedPage, transport) {
  return queryNearby(
    {
      customerId: displayedList.customerId,
      location: displayedList.location,
      page: requestedPage,
    },
    { transport },
  );
}
```

本题只交付 `solution.mjs` 和本说明，未修改真实工程。工程接入时，查询实现及自身契约可归属已有查询单元的 `queryNearby.ts`、`types.ts` 和小型 `index.ts`；刷新组合及其类型归属已有列表场景的 `refreshNearby.ts`、`types.ts`，通过查询公开入口调用。等待选择保留在交互代码。输入校验保留私有普通函数，不为此增加服务类、共享状态、注册中心或空角色文件；具体路径须按真实工程现有单元接入。

已执行：通过 Node.js 直接导入交付的 `solution.mjs`，使用 `node:assert/strict` 和可替换的定位、传输依赖执行 **11 组行为检查，全部通过**。其中缺参检查覆盖 17 个无效样本。

| 调用次序与反例 | 已验证结果 |
|---|---|
| 有效查询指定第 4 页，返回还有第 5 页 | 只请求第 4 页一次，原样返回对象，不自动追加页；条目缺展示字段也保留 |
| 缺客户、位置、页号，或空客户、非有限坐标、非正整数页 | 返回 `invalid-input`，不读取任何依赖 |
| 坐标为 `(0, 0)` | 正常请求，不误判缺参 |
| 查询依赖对象含会抛错的场景、草稿、缓存、交互、定位 getter | 查询成功且不触碰这些依赖 |
| 刷新时旧位置仍有效 | `location.read → query(newLocation, page: 1)` |
| 连续两次刷新 | 两次都重新定位，各使用对应新观测 |
| 定位 Promise 尚未完成 | 没有提前发起传输请求 |
| 普通翻页指定第 3 页 | 使用本次列表客户及位置，只调用一次传输，无定位依赖 |
| 客户选择 Promise 尚未完成，然后选择客户 | 等待时只有选择调用；之后顺序为选择、定位、该客户第一页查询 |
| 查询传输失败 | 查询和刷新均传播同一个异常对象 |
| 刷新定位失败且旧位置可用 | 传播同一个定位异常，不查询、不回退旧位置 |

未执行 TypeScript 工程检查、页面接线、真实网络、设备验证或 CI。真实接入后的验证范围是查询及刷新组合的现有消费者、刷新/翻页/等待选择入口的实际接线，并按工程门禁运行类型检查和相关测试；涉及定位适配变化时再补真机权限与设备行为。该改动未引入模型任务，不以本地替身检查声称完成真实业务联调。
