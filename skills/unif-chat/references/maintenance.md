# Chat UI 开发与接入

实现或使用 @unif/react-native-chat 的消息、列表、输入、附件、确认和过程展示时读取。源码维护采用库内 docs/DEVELOPMENT.md 指定的工程规范。应用只组合已提供组件时，沿用应用自己的规则。

## 按变化定位契约

| 本次变化 | 规范源中的入口 |
|---|---|
| 库归属、组件划分、Markdown 与公共依赖 | `libraries/react-native-chat.md` |
| 共享展示类型、动作和事件约定 | `libraries/react-native-chat/contracts.md` |
| 消息与列表 | `libraries/react-native-chat/message.md`、`message-list.md` |
| 输入与附件 | `libraries/react-native-chat/composer.md`、`attachments.md` |
| 确认、建议与过程 | 同目录 `confirmation.md`、`suggestions.md`、`process.md` |
| 来源、引用与反馈 | 同目录 `sources.md`、`citation.md`、`feedback.md` |
| 可选 Chat 组合、主聊天／抽屉及宿主接线 | 同目录 `chat.md`、`composition.md` |

以上路径相对于工程采用的规范根目录，不是其他技能的私有文件，也未随本技能分发；省略目录的文件均位于 `libraries/react-native-chat/`。只读取本次单元及实际依赖的契约；涉及 Design 公开接口时核对其公开资料，已安装 unif-design 时可按其入口定位。

## 开发边界

通用聊天 UI 属于独立 Chat 库。Portal 的消息投影、草稿、任务选择、确认对象、请求与结果采用留在 app 或所属领域；设备采集、附件准备、上传和 Agent 通信通过各自能力与接入完成。

组件接收展示数据，通过事件交出用户操作。输入、点击确认、回调返回或按钮动画结束不自行清空业务草稿、提交业务或生成成功状态。消息列表维护自己的显示与滚动，不保存会话事实或执行历史请求。

可选 Chat 组合使用独立组件，独立组件不反向依赖 Chat。业务卡片通过内容或公开渲染回调组合，库不按订单、拜访或工具名称内置业务分支。组件不导入 Portal 的私有类型、store、导航或日志实例。

基础 UI、主题与字体复用 Design；Markdown 采用实际选用的渲染器及必要薄适配。流式 UI 消费外部已提供的文本与状态，不接管 SSE、续推理或重试。库中的渲染类型不作为模型的业务协议。

导入名称、props、ref 与默认值按采用版本的公开类型核对。架构中的目标组件和目标扩展可以指导库开发，不能直接当作当前安装包的可调用 API；不沿用旧 Portal 的组件清单或私有导入路径补齐缺失接口。

## 验证

按本组件验证展示、事件、受控值与局部状态，再核对真实场景的数据投影和结果接收。输入、列表、图片和 Modal 组合补相应主题、字号、键盘与目标平台验证；附件资源与业务提交由其拥有方验证，不因共享聊天 UI 默认重跑全部业务流程。
