<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 ../source.json。 -->

# Portal 工程目录与基础代码组织

本文定义 React Native Portal 客户端的目标代码归属、公共入口、共用单元和测试组织，供模块开发、维护、重构与代码审查使用。原生 ArkTS／ArkUI 应用及 HAR 库的目录与 UI 归属见[鸿蒙工程组织](https://github.com/unif-design/unif-platform-architecture/blob/main/HARMONY_STRUCTURE.md)。系统职责、业务成功判定、状态归属和模型参与边界遵循[平台架构](https://github.com/unif-design/unif-platform-architecture/blob/main/ARCHITECTURE.md)；领域内容在各自架构和模块契约中维护。

通用目录职责、文件拆分、变量作用域和命名遵循目标工程已采用的规范；Portal 的采用关系见[文件变更入口](scope.md#1-文件变更入口)。本文只补充具体目录、依赖与业务契约。

目录用于定位职责，不表示功能已实现或需要立即新增。开发与维护以当前实现和实际调用为基础，复用已有组件、工具与能力，按本次需求补齐业务及接入缺口。能力边界见Portal 基础能力架构（规范源相对路径：`capabilities/portal-foundation.md`），实现与验收状态从当前源码及所属记录核实。


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
│   │   ├── marketing/         # 营销业务的应用接线与跨场景协调
│   │   │   ├── customer/      # 客户选择与结果展示的应用接线
│   │   │   ├── product/       # 选品、简称确认与识别展示接线
│   │   │   ├── visit/         # 拜访入口、应用宿主和场景生命周期
│   │   │   └── order/         # 共用订单入口、窗口与展示接线
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
│   │   ├── sqlite/
│   │   ├── keyValue/
│   │   ├── ble/
│   │   ├── share/
│   │   ├── permissions/
│   │   ├── deviceInfo/
│   │   └── system/
│   ├── domains/               # 领域内的功能、场景组合与业务交互
│   │   └── marketing/
│   │       ├── customer/      # 共用客户查询、资格、供货关系与展示
│   │       ├── product/       # 共用商品查询、选品与简称记忆
│   │       ├── visit/         # 拜访专属能力、流程、任务组合与卡片
│   │       ├── order/         # 共用订单草稿、输入、流程与提交
│   │       └── freezer/       # 共用冰柜资产、匹配、巡检与详情面板
│   ├── integrations/          # 外部系统或协议的客户端接入
│   │   ├── http/              # 传输、请求凭证接线
│   │   ├── agent/             # 超级智能体统一入口及流式传输适配
│   │   ├── memory/            # 公用记忆服务的客户端接入
│   │   ├── oss/               # 平台 STS、用途白名单与宿主目录适配
│   │   ├── speech/            # 语音凭证 HTTP 与身份适配
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

营销领域按业务归组，`customer`、`product`、`visit`、`order`、`freezer` 位于同一级；共同读写接入和查询辅助继续按其公共职责维护。拜访通过原公共接口复用订单与巡检，不能在拜访内部复制草稿、提交、扫描或匹配流程。领域卡片随其业务子单元维护，应用入口保留聊天、导航、日期与实例生命周期的接线。`app/marketing` 中跨拜访、下单的会话协调仍由共同组装持有；归组不合并业务状态，也不改变现有接口、数据和恢复契约。

应用已有规范的采用范围、根依赖与身份生命周期见Portal 应用组装（规范源相对路径：`app/portal.md`）；智能小 U 的明确打开动作、会话与领域结果接线见应用对话（规范源相对路径：`app/chat.md`）。这些组合复用下层契约，不将服务端内部设计作为客户端的初始化前置。

Portal 工程采用以下具体配置约定；通用文件角色与工具用法由工程标准维护：

| 内容 | Portal 采用 |
|---|---|
| 自有库版本范围 | 使用 `^`，锁文件记录实际安装版本 |
| 源码与测试别名 | `@/` 对应 `src/`，`@tests/` 对应 `__tests__/`；TypeScript、运行转换与测试解析保持一致 |
| 测试组织 | `__tests__/` 对应 `src/` 职责，实际共用辅助放 `_helpers/` 或 `_fixtures/` |
| Web 预览 | 使用项目实际采用的预览入口，核对已有展示与接入约束，组件接线按已确认的预览范围验收 |
| 功能说明 | 指向所属架构、模块契约与代码入口，工程说明记录 Portal 实际运行与接线 |
