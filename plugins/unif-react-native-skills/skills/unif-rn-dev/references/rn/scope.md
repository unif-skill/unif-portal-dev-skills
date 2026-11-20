<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 ../source.json。 -->

# Portal 文件开发规则

本文维护 Portal 客户端的项目采用与专属约定。代码组织、RN 实现、测试设计和技术文档分别采用 `uni-code-organization`、`uni-rn-dev`、`uni-test-design` 和 `uni-documentation`，具体版本与可访问来源由工程入口指明。目录归属见[目标目录](directory.md#1-目标目录)，能力边界见基础能力架构（规范源相对路径：`capabilities/portal-foundation.md`），业务契约与状态原则见[平台架构](https://github.com/unif-design/unif-platform-architecture/blob/main/ARCHITECTURE.md)。

本文是 React Native 客户端工程规则。原生 ArkTS／ArkUI 应用与库使用[鸿蒙开发规则](https://github.com/unif-design/unif-platform-architecture/blob/main/HARMONY_DEVELOPMENT.md)和[鸿蒙工程组织](https://github.com/unif-design/unif-platform-architecture/blob/main/HARMONY_STRUCTURE.md)；不把 TypeScript 文件名或 React Native 目录套用到这些工程或 Agent、Channel、CLI 的其他语言实现。开发与维护按[平台架构第 1.1 节](https://github.com/unif-design/unif-platform-architecture/blob/main/ARCHITECTURE.md#11-设计依据与适用范围)核对现有能力、有效契约和实际消费者，优先复用或在所属实现扩展；修改限定在本次功能及实际影响范围内。


## 1. 文件变更入口

在 Portal 客户端开发、测试、审查或交付源码及配套文件时，按工程入口取得已采用的通用规范及本次相关的 Portal 约定。新模块、公共契约、状态归属或场景职责需要设计时，取得相应设计依据；已有契约下的内部等价修改不重复开展完整架构设计。

开发前定位本次功能契约、所属单元、已有公开入口、实际消费者和对应测试。新增文件落在已确定的单元中；新增单元时说明其独立职责和使用方，不从页面名称或 SDK 包名直接推导一套业务模块。

工程提供设计与开发状态表时，先核对本次条目的范围、设计依据、适用规范、执行归属及具体限制，再读取对应契约。设计完成不等于代码已实现或已验收；未核对不等于未开始。状态表只作范围与依据索引，不替代契约正文、当前任务授权或真实验证证据。

设计、契约与工程约束齐备的单元可在授权范围内独立实施；未决项仅限制依赖它的部分。状态登记与有效依据不一致时更新登记，已有契约下的等价调整沿用原设计。规范和模块契约从工程指定入口取得并核对采用版本。

实现范围以有效需求和契约为边界。新增重试、自动提交、缓存、恢复、确认或接口调用等行为须有明确授权。


## 2. 各类代码的开发规则

Portal 具体归属见[目标目录](directory.md#1-目标目录)。在工程已采用的职责与依赖规则上补充以下项目约定：

| 单元 | Portal 约定 |
|---|---|
| components | 优先使用 Design、Chat 及当前工程共用组件；确认 UI 的采用结果由所属场景处理 |
| capabilities | 按所属能力契约接入 SDK，保留调用、取消、资源和平台责任 |
| domains | 页面和对话复用所属领域链路；最终业务规则与事实由业务系统处理 |
| integrations | 按所属协议及真实接口码表转换 DTO、请求和结果，不补造身份或业务成功 |
| app | 账号、设置、对话各自维护状态；bootstrap 与导航负责真实组装 |
| hooks、utils、config、types | 采用通用文件规则；Portal 配置、业务存储和资源的具体归属见[工具与文件归属](utilities-config.md#3-工具常量类型及其他文件的归属) |

测试、脚本与原生配置沿用实际工程工具，不套用手工 TypeScript 单元的文件名。

### 2.1 可订阅状态

Portal 自有可订阅状态统一使用已采用的 `zustand/vanilla` store，按所属功能与实例生命周期创建，不手写订阅者集合和状态发布机制。持久化顺序、敏感数据边界和身份隔离遵循所属契约；SDK 事件使用其公开订阅接口。
