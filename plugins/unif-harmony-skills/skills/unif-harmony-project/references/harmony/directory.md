<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。来源与章节见 ../source.json。 -->

# Unif 原生鸿蒙工程组织

本文定义 Unif ArkTS／ArkUI 应用、原生库和共享资源的职责归属。项目采用见[适用范围](scope.md#1-适用范围与实施)，状态与验收分别见[状态与生命周期](state.md#3-arkui-状态与生命周期)、[验证与交付](testing.md#5-验证与交付)，系统职责见[平台架构](https://github.com/unif-design/unif-platform-architecture/blob/main/ARCHITECTURE.md)。下列目录是 Unif 的组织约定，按真实职责使用，不是必须预建的文件清单。


## 1. 工程目录与依赖

应用沿用 Stage 工程与实际模块配置；在所属模块的 `src/main/ets/` 下按需要组织：

| 单元 | 责任与依赖 |
|---|---|
| `app/` | 启动、导航、依赖组装及账号、设置、聊天等应用功能；各功能维护自己的状态 |
| `components/` | 跨功能的展示与交互；消费输入、事件和主题，不直接读取业务状态或发请求 |
| `capabilities/` | 设备与本地操作、取消和资源交接；优先消费已有库公开能力 |
| `domains/` | 所属业务功能、准备／确认／提交及场景组合，复用当前业务契约 |
| `integrations/` | HTTP／SSE／H5 等外部协议、DTO 与转换；不决定额外业务流程 |

应用入口组装上述单元；`components/`、`capabilities/` 和六库不反向读取全应用状态对象。

Portal（原生鸿蒙）在 `ai-app-portal-harmony/packages/` 按包维护 HAR 模块。每包声明包名、版本和公开入口，自行声明依赖并携带所需资源。宿主通过本地模块依赖引用包名及公开子路径。有独立分发需求时，可从同仓模块发布 OHPM 版本。使用方切换依赖来源并更新锁文件，保持相同的公开导入。

Icons 负责图标，Design 负责主题及通用 UI，Chat 负责聊天呈现组合；Camera、Scan、Umeng 负责各自能力和必要 UI。应用账号、业务请求、草稿和上传流程不搬入库，库不依赖 Portal 私有代码。具体包是否存在、互相依赖哪些组件，以当前工程核实。

六库的 ArkUI 示例与实际应用消费同一套公开能力；各库验收覆盖本库实际采用场景。
