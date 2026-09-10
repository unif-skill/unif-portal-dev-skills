# 刷新、查询与交互的调用边界

本题是合成架构审查，接口名和数据只在本题成立。给出简短设计结论、必要 TypeScript 契约和可运行的 `solution.mjs`，不要修改真实工程或安装依赖。

客户附近列表已有一次位置观测和已显示结果。已确认行为：用户明确点击刷新时重新获取当前位置，再按本次客户查询第一页；不能因旧位置仍可用跳过重新定位。普通翻页由用户点击下一页，沿用本次列表的位置和客户，读取指定页。客户尚未选定时，交互可以等待选择；列表能力还会被无 UI 的调用方使用。后续业务操作的选择与确认属于已有交互，不是本次查询的一部分。

合成公共函数保持以下名称和可调用形式，具体依赖范围由你审查：

- `refreshNearby({ customerId, previousLocation }, deps)`：执行本次刷新，返回 `{ location, result }`。`deps.location.read()` 返回 `{ latitude, longitude }`；`previousLocation` 是可能存在的旧观测。
- `queryNearby({ customerId, location, page }, deps)`：客户、位置和正整数页号是必需输入，缺少必要输入返回 `{ kind: 'invalid-input' }`。传入条件满足时读取一页，结果沿用 `deps.transport.query(input)` 返回的 `{ kind: 'success', items, nextPage? }`。传输异常原样传播。

现有统一运行环境还可提供 `scene.currentCustomer()`、`draft.read()`、`cache.get()`、`interaction.requestCustomer()`、`interaction.confirm()`。有人提议把它们都传给查询：缺客户时选当前客户，缺坐标时自行定位，有缓存时直接返回，无缓存则自动拉完全部页再询问确认。理由是查询无写入，可以在能力内部统一节省调用。

请审查这个提议并产出两个真实可调用的导出函数；不要只输出一套脱离代码的边界口号。说明刷新、缺参、翻页、等待选择与确认各由谁触发和准备输入，公共查询实际需要哪些依赖。列出能验证这些结论的调用次序与反例；示例中可以使用普通私有函数，不要求实现完整 UI。
