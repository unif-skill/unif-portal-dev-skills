# 刷新、查询与交互的调用边界

不采纳将统一运行环境全部传给查询的提议。查询无业务写入，并不意味着可以替用户选择输入、改变刷新语义、扩大分页范围或启动确认。`solution.mjs` 已实现两个具名导出：`refreshNearby` 和 `queryNearby`。

| 行为 | 触发与输入准备 | 实际执行 |
| --- | --- | --- |
| 明确刷新 | 刷新入口确定本次客户；尚未选择时由已有交互等待选择 | `refreshNearby` 每次先调用 `location.read()`，等待新观测，再以本次客户、新位置和 `page: 1` 调用 `queryNearby` |
| 缺必要输入 | 无 UI 调用方负责提供客户、位置与页号；交互入口可以在调用前补齐 | `queryNearby` 返回 `{ kind: 'invalid-input' }`，不访问任何依赖，不自行等待或补参 |
| 下一页 | 用户点击下一页；入口取本次已显示列表对应的客户、位置及指定页号 | 直接调用 `queryNearby` 一次；保留返回的 `nextPage`，不自动追页，不重新定位 |
| 等待选客户 | 已有入口或组合函数调用 `interaction.requestCustomer()` | 选择完成后把客户标识显式传给刷新；等待期间不发起定位或查询，未选定则不继续 |
| 后续业务选择与确认 | 原有后续业务交互根据用户动作触发 | 不属于这两个函数，不向查询注入 `interaction.confirm()` |

`previousLocation` 为兼容既定调用形式保留，但本次刷新不读取、不比较也不回退使用它。定位失败向调用方传播，不能凭旧位置继续冒充成功刷新。列表入口维护本次列表的客户与位置快照；即使别处的当前客户变化，普通翻页仍使用该列表快照。已有页面负责接收结果、展示和异步交互状态，本题不新增公共状态机制。

公共查询的唯一外部依赖是 `transport.query`。刷新组合只需要定位读取和查询传输；它通过调用真实的 `queryNearby` 完成第二步，并只把查询需要的传输依赖交给它。`scene.currentCustomer()`、`draft.read()`、`cache.get()`、`interaction.requestCustomer()` 和 `interaction.confirm()` 均不进入查询依赖。

缓存命中直接返回会跳过题目要求的本次读取，自动追页会把“一页”改成“全部页”，旧位置可用就跳过定位会破坏刷新。调用数应按相同业务行为衡量：刷新一次定位加一次单页请求；有效普通查询一次请求；缺参查询零请求。等待选择的时间归交互等待，不能据本地替代依赖测试宣称真实端到端耗时降低。

## 必要 TypeScript 契约

本合成契约将客户标识定义为非空字符串、坐标定义为两个有限数值，页号为正整数。无额外地域范围、业务准入判断，也不转换传入标识。TypeScript 字段保持必填；运行时无效输入返回值用于保护 JavaScript 等动态调用边界。

```ts
export interface LocationObservation {
  latitude: number;
  longitude: number;
}

export interface QueryNearbyInput {
  customerId: string;
  location: LocationObservation;
  page: number;
}

export interface NearbySuccess<Item> {
  kind: 'success';
  items: Item[];
  nextPage?: number;
}

export interface InvalidInput {
  kind: 'invalid-input';
}

export type QueryNearbyResult<Item> = NearbySuccess<Item> | InvalidInput;

export interface NearbyTransport<Item> {
  query(input: QueryNearbyInput):
    NearbySuccess<Item> | Promise<NearbySuccess<Item>>;
}

export interface QueryNearbyDeps<Item> {
  transport: NearbyTransport<Item>;
}

export interface LocationReader {
  read(): LocationObservation | Promise<LocationObservation>;
}

export interface RefreshNearbyInput {
  customerId: string;
  previousLocation?: LocationObservation;
}

export interface RefreshNearbyDeps<Item> extends QueryNearbyDeps<Item> {
  location: LocationReader;
}

export interface RefreshNearbyResult<Item> {
  location: LocationObservation;
  result: QueryNearbyResult<Item>;
}

export declare function queryNearby<Item>(
  input: QueryNearbyInput,
  deps: QueryNearbyDeps<Item>,
): Promise<QueryNearbyResult<Item>>;

export declare function refreshNearby<Item>(
  input: RefreshNearbyInput,
  deps: RefreshNearbyDeps<Item>,
): Promise<RefreshNearbyResult<Item>>;
```

`transport.query` 的成功对象原样返回，包含 `items` 和可选 `nextPage`；传输抛出的异常原样传播。定位异常也直接传播。实现不把失败投影成空列表，不自行重试。定位适配若违反约定返回缺字段对象，查询判为无效输入，不使用旧位置补字段。

## 文件方案

本次实际交付只有本说明和可由 Node.js 直接导入的 `solution.mjs`；其中校验是普通私有函数，不扩大公共接口。

若落入真实 Portal，先在既有附近列表所属单元核实现有公开入口与消费者，再映射为 `nearby/types.ts`、`nearby/queryNearby.ts`、`nearby/refreshNearby.ts` 和必要的小型 `index.ts`。类型放 `types.ts`，查询文件保留私有输入校验，刷新文件承担组合，公开出口仅暴露实际消费者所需函数与契约。交互事件处理继续属于已有列表交互单元，不新增通用运行环境、辅助类、统一 store 或无内容的角色文件。此处未检查真实仓库，因此这些是相对单元方案，不是已确认的项目绝对路径。

## 验证证据与反例

已执行：使用 Node.js 内置 `node:assert/strict`，直接导入实际 `solution.mjs`，完成 11 组行为检查，全部通过；未复制实现作为被测替身。网络和定位使用可记录事件的替代依赖，额外环境成员使用会抛错的 getter 检查禁止访问。

| 已执行检查 | 调用次序或反例及断言 |
| --- | --- |
| 缺参和输入结构 | 18 种无效输入，包括缺客户、缺坐标、非有限坐标、缺页号、零、负数和小数页号；均返回 `invalid-input`，所有依赖零访问 |
| 无 UI 单页查询 | 零经纬度合法；请求指定第 4 页一次，结果带 `nextPage: 5` 也不继续；成功对象保持引用，额外环境与定位依赖均未访问 |
| 查询传输失败 | 抛出同一个错误对象，不包装、不吞掉 |
| 旧位置存在的刷新 | `location.read → query({ 本次客户, 新位置, page: 1 })`；返回新位置和传输原结果，旧对象未修改 |
| 连续刷新 | 即使旧位置等于返回位置，两次刷新仍定位两次、查询两次 |
| 不依赖旧位置 | `previousLocation` getter 一访问就抛错，刷新仍成功 |
| 异步定位次序 | 定位 Promise 未完成前查询次数为零；完成后才读取第一页 |
| 定位失败 | 有旧位置仍原样抛错，查询零次 |
| 刷新中的传输失败 | 保留原错误对象 |
| 新观测不符合契约 | 返回缺坐标的新观测时，查询结果为 `invalid-input`，传输零次，没有旧位置回退 |
| 入口等待与普通翻页 | 私有交互示例先等待 `requestCustomer`，等待期间定位和查询均为零；选定 A 后定位并查询第 1 页。外部当前客户再改为 B，点击第 3 页仍以列表快照中的 A 与原位置查询；没有再次定位或确认 |

这些反例能区分“查询返回看似正确”与“调用边界正确”：只检查最终列表，无法发现暗中补客户、跳过定位、缓存替代、追页或多余确认。

拟执行的真实工程验证：定位实际查询消费者（包括无 UI 调用方）及刷新、翻页入口，检查导入和 TypeScript 契约，再运行这些消费者和组合的定向测试。只有实际修改了传输适配、设备接线或共享契约，才相应扩大接口联调、原生定位验证和受影响消费者范围。本题未运行 TypeScript 编译、真实 UI、网络接口、设备定位或仓库 CI；上述本地结果不证明这些层面已完成。
