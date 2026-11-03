<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 ../source.json。 -->

## 2. 基础组件与 UI 复用

### 2.1 复用来源

| 内容 | 使用与维护位置 |
|---|---|
| 基础按钮、输入、列表原子、主题、颜色与图标尺寸 token | 通过 `@unif/react-native-design` 的公开入口使用，版本由工程依赖锁定 |
| 图标组件及 IconProps 类型 | 通过独立 `@unif/react-native-icons` 的公开入口使用，主题、尺寸和交互由控件或实际消费者提供；具体边界见Icons 契约（规范源相对路径：`libraries/react-native-icons.md`） |
| 通用图片预览、Sheet 内容布局、动作菜单内容与受控编辑／短信输入 | 直接使用 Design 的 ImagePreview、Sheet、ActionMenuContent、TextEntryContent、SmsField；应用宿主、业务值与资源持有留 Portal |
| Portal 自有、可跨场景使用的页面布局、列表组合及键盘交互 | `components/` 中的对应单元 |
| 消息气泡、附件展示、输入区、确认展示等聊天 UI | 通过独立 `@unif/react-native-chat` 的公开入口使用；库基于 design 开发，Portal 保留场景组合与数据／事件适配 |
| 消息 Markdown 渲染 | 复用第三方渲染库，chat 维护必要的主题与交互薄适配；分包条件见库设计（规范源相对路径：`libraries/react-native-chat.md#5-分包建议与维护成本`） |
| 键盘容器、输入区域避让和关联 hook | `components/keyboard/`；状态只服务于键盘布局与交互 |
| 账号、首页、设置等特定应用功能的表单或组件 | `app/` 下的所属功能 |
| 客户、订单、拜访等业务卡片和表单 | 所属领域模块的交互代码 |
| 相机宿主、地图视图等与设备能力直接相关的 UI | 所属 `capabilities/` 单元 |
| WebView 与 H5 协议处理 | `integrations/h5/` |

Portal 的设计系统由 Design、Chat 等所属库维护，应用不维护同名 Button、Input 或主题 API。Portal 自有适配承接本项目的宿主接线、协议结果与资源交接；旧工程曾使用的依赖不自动成为新工程选型。

现成展示组件可在所属 UI 或场景组合中直接使用。已经定义 Portal 功能契约的设备操作由其所属实现接入 SDK，各入口复用该功能公开接口；例如拍摄的调用归属与媒体交接遵循拍摄契约（规范源相对路径：`capabilities/camera.md`），不能因“直接使用 SDK”而在各页面重新实现。Portal 自有的组合组件与交互适配按已确认行为及新契约重写，完成后供新工程的多个入口复用。

Portal 共用组件不查询客户、提交订单或保存会话。确认组件只展示内容与交付动作；客户、下单、拜访等场景决定确认对象、动作含义与后续业务。

导航相关的页面布局与弹层保留其视觉和交互用途，路由参数、页面注册与具体导航动作由入口适配。普通页面通过 ScreenHeader（规范源相对路径：`components/screen-header.md`） 将标题和操作交给原生导航栏，滚动内容使用导航库的透明与原生避让能力。主题和键盘 Provider、Toast 等应用所需宿主由应用组装。

公共内容采用 Design 的 Sheet（规范源相对路径：`components/sheet.md`）和图片预览（规范源相对路径：`components/image-preview.md`），键盘处理采用 Portal 的键盘视口（规范源相对路径：`components/keyboard.md`）。ScreenLayout、HtmlContent 等按所属工程契约使用；相近展示直接组合 Design 足够时，不为目录示例再创建一层组件。紧凑进度文案与其文字动效由 Chat 的 ProcessingProgress 提供，进度来源和结束时机仍由原场景控制。

Portal 自有组件承接所属场景的交互或组合，保留已确认的中文展示、主题与可访问性要求。客户、订单、拜访的专属卡片继续由领域维护。

### 2.2 聊天 UI 与业务逻辑

聊天展示由独立的 @unif/react-native-chat（规范源相对路径：`libraries/react-native-chat.md`） 维护，主聊天和业务抽屉通过公开入口按需要组合相同组件。库的基础 UI、主题和字体复用 @unif/react-native-design；展示契约属于库，通过 props、children 或已有渲染回调接收内容并交付用户操作。服务端流事件到展示数据的转换留在 `integrations/agent/` 与 `app/chat/` 各自负责的接入、交互代码中；领域卡片和专属编辑区由所属领域提供，不移入聊天库。

主聊天和业务抽屉分别按所属场景持有输入草稿、业务状态与结果采用责任；共用 Chat 不合并它们的消息列表，也不决定是否另建服务端会话。已有引用按相应会话与场景契约交接。

语音、拍摄、文件选择、附件准备和 Agent 通信复用对应公共功能，场景只保留参数、处理时机和业务交接等实际差异。任务内容和合法结果范围由场景／运行代码按契约选择，提示词留在所属任务模块，基础组件不通过 prompt 或业务模式分支执行领域流程。采用普通组件组合及已有函数即可。

组件名称中的 Message、Task、Tool、Confirmation 等只描述展示用途，不赋予组件发起模型、工具或业务调用的职责。可选回调只在所属场景已经定义该动作时接入，不能因为组件支持一个按钮就新增重试、提交或其他操作。

### 2.3 局部交互与订阅边界

选品结果仍交原 OrderFlow 采用／拒绝，答案仍交原问题处理；局部 UI 不复制订单、拜访或对话的业务草稿。

订阅调整保留客户、数量、价格、版本、资格及工作流变化的原有发布与协调。局部交互结果仍交所属业务目标；账号或目标切换后的失效处理，以及临时隐藏与业务结束的区别，按所属场景契约核对。
