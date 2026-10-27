<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 source.json。 -->

# Portal 工程目录与基础代码组织

本文定义 React Native Portal 客户端的目标代码归属、公共入口、共用单元和测试组织，供工程初始化、模块开发与代码审查使用。原生 ArkTS／ArkUI 应用及 HAR 库的目录与 UI 归属见[鸿蒙工程组织](../SKILL.md)。系统职责、业务成功判定、状态归属和模型参与边界遵循平台架构（规范源相对路径：`ARCHITECTURE.md`）；领域内容在各自架构和模块契约中维护。

新增或修改文件时的分类规则、角色文件拆分、变量作用域和命名规范见[Portal 文件开发规则](../SKILL.md)。

目录用于定位职责，不表示每项都要立即实现。基础能力设计通过阅读旧 Portal 的全部相关代码和消费者，核对现有用途与处理结果，完整边界见Portal 基础能力架构（规范源相对路径：`capabilities/portal-foundation.md`）；业务流程与服务端接入按实际交付补齐所需契约。新工程的自有组件、工具与支撑代码按目标职责重写，行为核对入口见现状行为与目标职责对照（规范源相对路径：`notes/portal-foundation-inventory.md`）。


## 1. 目标目录

```text
Portal/
├── App.tsx                    # React 根组件，调用 app 中的组装代码
├── index.ts                   # 应用注册与启动接线
├── src/
│   ├── app/                   # 启动、导航、依赖组装及应用自身的功能入口
│   │   ├── bootstrap/         # 初始化、必要宿主和资源清理的接线
│   │   ├── navigation/        # 路由注册、导航参数与导航适配
│   │   ├── presentation/      # 根、导航页面及原生窗口共用的能力宿主组装
│   │   ├── account/           # 账号与登录相关功能、交互、状态和接入
│   │   ├── home/              # 应用首页与应用选择
│   │   ├── settings/          # 应用设置、主题偏好等
│   │   ├── configuration/     # 业务系统提供的应用配置及其客户端状态
│   │   ├── policy/            # 应用协议内容与相关交互
│   │   ├── qrCode/            # 明确内容的通用二维码展示与返回
│   │   └── chat/              # 对话入口、客户端交互及业务结果接线
│   ├── components/            # 可复用的展示与交互组件
│   │   ├── ScreenHeader/
│   │   ├── ScreenLayout/
│   │   ├── CellList/
│   │   └── keyboard/          # 键盘交互组件、hook 与必要运行状态
│   ├── hooks/                 # 无业务归属的通用 React hook
│   ├── capabilities/          # 设备、本地存取等独立能力
│   │   ├── camera/
│   │   ├── imagePicker/
│   │   ├── documentPicker/
│   │   ├── scan/
│   │   ├── location/
│   │   ├── places/
│   │   ├── map/
│   │   ├── sqlite/
│   │   ├── files/
│   │   ├── keyValue/
│   │   ├── ble/
│   │   ├── share/
│   │   ├── voice/
│   │   ├── permissions/
│   │   ├── deviceInfo/
│   │   ├── system/
│   │   └── logger/
│   ├── domains/               # 领域内的功能、场景组合与业务交互
│   │   └── marketing/
│   ├── integrations/          # 外部系统或协议的客户端接入
│   │   ├── http/              # 传输、请求凭证接线
│   │   ├── agent/             # 超级智能体统一入口及流式传输适配
│   │   ├── memory/            # 公用记忆服务的客户端接入
│   │   ├── oss/               # 文件上传与凭证接入
│   │   ├── speech/            # 语音识别协议接入
│   │   └── h5/                # H5 协议、WebView 容器与桥接适配
│   ├── utils/                 # 无业务状态的通用计算与格式处理
│   ├── config/                # 构建环境、应用品牌等应用配置
│   ├── assets/                # 应用共用静态资源
│   └── types/                 # 确有需要时的环境、资源或第三方补充声明
├── __tests__/                 # 按 src 中的责任归属定位测试
│   ├── components/
│   ├── hooks/
│   ├── capabilities/
│   ├── domains/
│   ├── integrations/
│   ├── app/
│   ├── utils/
│   ├── config/
│   ├── integration/           # 跨功能组合与真实接线验证
│   └── _helpers/              # 实际共用的渲染、替身和测试辅助
├── android/                   # Android 原生工程与配置
├── ios/                       # iOS 原生工程与配置
└── scripts/                   # 工程检查和构建所需脚本
```

图中组件为目标工程的共用单元示例，现状行为的阅读来源与目标职责在对照文件中。通用聊天组件由独立的 @unif/react-native-chat（规范源相对路径：`libraries/react-native-chat.md`） 提供，消息所需 Markdown 复用第三方渲染器及必要适配，不在 Portal 的默认目录中另设一套实现。基础能力按现有用途完整纳入设计，开发顺序由具体实施批次决定，目录在对应代码进入工程时创建。不能以尚未排入某一批开发为由省略能力、消费者或目标归属；这些归属不表示将旧文件逐一搬入新目录。

`app/` 中的账号、首页、设置和对话入口各自维护自己的功能与交互，不共用一个覆盖全应用的状态对象。`bootstrap/`、根组件与导航注册承担全应用依赖接线，`presentation/` 维护它们共用的静态能力宿主组合；下层代码不依赖这些组装实现。领域专属页面和卡片留在 `domains/<领域>/`，由应用导航或对话入口接入。

应用已有规范的采用范围、根依赖与身份生命周期见Portal 应用组装（规范源相对路径：`app/portal.md`）；智能小 U 的明确打开动作、会话与领域结果接线见应用对话（规范源相对路径：`app/chat.md`）。这些组合复用下层契约，不将服务端内部设计作为客户端的初始化前置。

组件或能力存在多个协同文件时使用目录；页面及其专用类型、样式和交互代码组成页面单元。使用 `screens/` 分类目录时，每个页面在其中维护自己的单元，跨页面共享的展示组件放在所属功能的 `components/`；页面私有组件留在页面单元内，跨功能通用展示组件归根 `components/`。组件实现与配套文件的拆分见[文件开发规则第 3.1 节](file-rules.md#31-固定文件角色)。通用工具可以是单个文件，不要求一个函数一个目录或每个单元都有相同文件集合。

工程配置与辅助文件也有固定归属：

| 内容 | 位置与职责 |
|---|---|
| 依赖与版本锁定 | 根 `package.json` 与工程采用的锁文件；只加入实际接入代码需要的包和运行依赖；自有库消费范围使用 `^`，锁文件记录实际安装版本 |
| TypeScript、编译与模块解析 | 根 `tsconfig.json`、`babel.config.js`、`metro.config.js`；`@/` 对应 `src/`，实际使用该别名的编译和测试入口保持一致 |
| 导入与代码检查 | 根 ESLint 配置及需要的 `scripts/` 检查；按本文的单元边界配置 |
| Jest 配置与运行环境 | 根 `jest.config.js`、`jest.setup.ts` 等实际需要的配置文件；平台替身只留在测试环境 |
| 测试数据与渲染辅助 | 单个用例的 fixture 随测试；确有共同消费者时放 `__tests__/_fixtures/` 或 `_helpers/` |
| Web 预览接入 | 按新工程采用的预览需求维护宿主、依赖和编译配置；旧 `website/` 用于核对展示行为与接入约束，新组件接线另行验证，原生测试不能证明 Web 接入正确 |
| 功能设计与开发说明 | 引用所属架构、模块契约和代码入口；工程内说明只补充实际运行与接线信息 |
