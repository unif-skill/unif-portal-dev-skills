# 模块接口、内部准备与查询交互

这是合成 Portal 工程。本题名称、依赖与协议仅作为评测材料，不代表实际 API 或项目开发批次。审查方案并交付 `response.md`、可运行的 `solution.mjs` 及 Node 内置测试 `solution.test.mjs`。不安装依赖、修改真实工程、调用网络或设备。

## 已有模块与协议

目录模块文档列出了公共 `prepareQueryClient`、`queryItems`、`pickItem`，查询输入/结果类型，以及可由两个交互入口复用的 `QueryPickerHost`。已采用的对外协议只有 `GET /catalog/items`，参数为 `{ keyword, page }`，返回 `{ items, nextPage? }`。本批没有新的 H5 消息或模型工具协议。

已明确的内部准备：`deps.client.prepare()` 完成普通客户端配置并返回具有 `get(path, query)` 的客户端；它不是 HTTP 请求，不需要用户确认。`queryItems(input, deps)` 每次在自身调用链中完成这项准备，再请求指定一页；消费者只需传完整的 `{ keyword, page }`。准备与请求异常原样传播，没有重试或额外请求要求。

交互选择入口调用 `pickItem(initialInput, deps)`。已有 `deps.picker.pick({ initialInput, query })` 负责显示、用户修改条件、翻页和选择；通过 query 回调取得所需页，最后返回选中的条目或 null。query 回调应复用同一个 queryItems 公共函数。只取数据的业务场景直接调用 queryItems，无需 picker 或已挂载的 QueryPickerHost。

保持上述三个公共函数名称和调用形式；prepareQueryClient(deps) 可以承载内部准备，但提取它不改变 queryItems 的使用前置条件。给出必要类型、纯数据与交互入口两条调用链，以及实际协议清单；JS 中实现这三个真实导出函数。

## 待审查建议

有人准备扫描模块的 export 列表，为两个查询函数分别生成 `/prepareQueryClient`、`/queryItems` 端点和对应 H5 消息、模型工具；再让所有调用方先调用 prepare 接口并确认准备结果，最后进入查询 UI，依赖 QueryPickerHost 挂载后才能获取数据。理由是模块已经公开这些函数与宿主，而且共用查询 UI 可以统一行为。

请判断哪些步骤由原调用链完成、哪些入口实际需要 UI，以及公共代码符号是否足以新增网络/桥/工具协议。测试应调用真实导出函数，仅替换 client 和 picker 边界，核对初始化与 HTTP 调用的区别、参数、顺序、次数和异常，不能仅复述规则。
