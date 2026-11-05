<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 ../source.json。 -->

## 4. 公共入口与依赖方向

Agent 客户端保留统一公开入口，按 transport、turns、observation、inputAttachments 处理传输、执行、观察与原件直传；运行控制类型和分析结果解码仍随所属功能维护。云会话目录、状态同步和内容投影实现退役。公共执行与业务契约采用同源生成物；类型通过 `import type` 从生成器维护的 `@/generated/contracts` 统一导入，不穿透 `protocol` 或 `types`。运行时校验采用 manifest 登记的 `@/generated/contracts/validators/<主题>/<契约>` 独立模块，避免全量目录进入 Metro bundle，不复制为手写定义。

本机会话、目录、运行关联及私有文件引用归 app/chat/recovery，SQLite 表与事务由该功能维护；不建立 app/chat/sync 或云 content 层。本机聊天契约源归 app/chat/contracts/schema.json，营销恢复源归 domains/marketing/recovery/schema.json，各自生成类型与严格校验。运行实例、草稿与业务 owner 仍按所属生命周期创建，冷恢复调用原构造流程，不保留公开热合并入口。

应用会话工厂可把订单创建、恢复采用、单会话装配和拜访入口协调提取为所属单元的私有实现。原工厂继续持有 store、实例表、取消信号和释放列表；提取代码引用这些原对象，可变标记实时读写原变量，不捕获一次快照或另建生命周期。私有入口按实际所有者登记导入检查，不因目录拆分扩大公共 API。

营销结果执行的客户、订单与拜访动作归 `marketingResult/actions`，主执行器保留依赖调度、业务成功等待和统一释放。`OrderFlowPanel` 的数量编辑与选品 Hook 随面板实例维护原有交互状态，互斥判断读取实时 ref；订单换品与待补编辑的纯计算归 `order/flow/edits`，状态采用、标识分配、缓存写入和确认通知仍由原 flow 执行。这些实现只由所属单元消费，不进入公共入口。

Portal 的应用组装连接各能力和协议实现，页面及对话入口调用所属场景；领域内查询保留领域归属。

启动层的会话凭据读取与 HTTP 授权接线归 `app/bootstrap/session`，继续复用账号控制器的身份范围及刷新策略；H5 授权、位置范围和日志身份投影归 `app/bootstrap/h5`。聊天草稿及其类型、语音反馈常量归 `app/chat/draft`，原会话工厂持有实例与释放责任。

公开入口保留加载边界：`app/voice` 只提供服务构造，采集 Hook 由 `app/voice/input` 提供；纯存储组合归 `app/settings/storage`，原生应用目录接线归 `app/settings/storage/app`。营销问题展示选择器和拜访历史投影分别归 `app/marketing/questions`、`app/marketing/visit/orderHistory`，只读展示不因入口汇总而提前加载会话工厂。

首页公告目录、预览、列表、详情与公共格式处理归 `app/home/notices`；公告根入口保留目录工厂，组件与页面通过各自目录接入。设置的日志、存储、记忆及主题字体页面分别随 `app/settings/logs`、`storage`、`memory`、`preferences` 维护，系统权限与关于页面仍在 `app/settings/screens`；功能根入口不重导出页面，原状态、实例与原生加载边界保持。

拜访照片预览组件统一命名为 `app/marketing/visit/VisitPhotoPreview`，同时服务当前与历史照片；历史问卷 Hook 归 `historyQuestionnaires`。领域出发卡内容归 `domains/marketing/visit/plan/VisitDepartureContent`，应用 `VisitDepartureCard` 保留聚焦、日期与实例接线。订单数量输入 key 的构造与校验归 `order/flow/orderQuantityInputKey.ts`，不改变数量草稿状态与恢复字段。

独立组件与供其他单元消费的功能提供小型 `index.ts`，显式导出实际使用的能力和类型。源码跨单元使用 `@/` 引用目标公开目录，测试跨目录辅助使用 `@tests/`；同单元及所属私有子实现保留相对导入，不从内部绕回自己的入口。`product` 等分类父目录不重复汇总子单元，已登记的私有工厂、共享样式、内部状态和底层适配保持原边界。平台专属测试、生成器内部引用及根配置资源沿用实际解析规则，不合并导出不同平台实现。

计划、任务及到店判断共享的坐标校验与距离计算归 `domains/marketing/visit/location`。计划和任务各自通过该公开入口复用，纯位置计算不反向加载计划或任务工厂。

Portal 源码文档沿用工程已采用的语言与注释规范；账号、会话、媒体及业务交接的说明以所属契约为准，核对调用语义和资源责任，不在注释中另设业务规则。

日志的常规调用与全局捕获安装、文件存取分别提供入口，组件记录日志只依赖常规调用入口。Sheet 与键盘 UI 等同层单元按所属契约形成必要的无循环依赖。

工程接线时同步 AGENTS.md、路径别名与现有导入检查。项目公开边界以本仓实际契约为准，不复制另一套全局业务类型或运行时注册框架。


## 5. 基础能力与资源归属

拍摄与媒体选择、定位与地点查询、地图与选点、SQLite 与文件存取、扫码、蓝牙、分享、语音及系统支撑的完整职责、组合和消费者在Portal 基础能力架构（规范源相对路径：`capabilities/portal-foundation.md`）维护。某项能力分散在页面、工具或业务目录中时，也按完整调用链纳入，不只盘点同名文件夹。

每项现有用途都要明确是独立能力、客户端组合、交互入口、领域适配还是未接入占位。普通功能与复杂组合可以在同一模块内分别验证；SDK 全集不等于产品需求，已有组合也不能因职责拆分而丢失。
