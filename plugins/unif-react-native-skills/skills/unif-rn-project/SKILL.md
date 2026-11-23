---
name: unif-rn-project
description: 在 Portal 的 React Native 应用或 @unif RN 库中，需要核对页面状态、环境配置、H5 交接或共享核心的实际消费者时使用。只查包版本或已有 API 时查看相应库资料。
---

# Unif React Native 工程

先找到用户操作经过的页面、Hook 或 H5 消息，再核对工程锁定的库版本。Portal 负责页面与业务交互，独立库的职责从公开入口和实际调用它的示例或应用确认。

## 从实际入口跟到结果

页面使用 Design、Chat 或设备能力时，沿回调找到最后修改草稿、提交订单或接收附件的代码。审查取消操作时，从用户按下按钮一直查到页面传给组件的函数。组件自身能渲染，只能证明这一层。选用组件与能力时查[UI 复用](references/rn/ui.md)，跨模块接线查[公开入口与宿主](references/rn/dependencies.md)。

异步操作要保留发起时的身份和登录周期。例如，同一账号退出再登录，第一次登录发出的请求仍属旧会话。用当前有效响应和迟到的旧响应分别验证页面或 store 的写回。涉及本地恢复和状态订阅时，查 [Portal 的状态采用](references/rn/scope.md)与 `$unif-platform-rules` 的 `references/architecture/state.md`。

H5 调用还需核对发送文档、授权和接收结果的文档。原生接受脚本、H5 真正收到消息、业务系统返回回执是三个可单独观察的结果。[H5 桥接](references/rn/h5-bridge.md)

## 选择受影响的工程和宿主

- **Portal 应用。** 文件移动时查[目录](references/rn/directory.md)、[文件规则](references/rn/file-rules.md)和[配置与存储](references/rn/utilities-config.md)。环境变更要查清原生构建选定的环境文件以及进程实际加载的值。按[Portal 验证](references/rn/testing.md)选择受影响的 iOS、Android 或 Web 接线。
- **独立库与共享核心。** 从[RN 库的工程采用](references/rn/project.md)定位锁定版本、包产物及实际使用者。分别核对共享逻辑、原生适配、宿主交互和业务回执。查库 API 时以采用版本的公开类型和库文档为准。

新增失败路径时，按 `$unif-platform-rules` 的 `references/architecture/verification.md#721-日志与故障诊断` 检查应用记录。跨模块取消、结果采用和业务成功按 `references/architecture/contracts.md` 及业务契约判断。已确定的跨仓字段变更使用 `unif-contract-change`。

## 按任务选择工程方法

| 当前任务 | 方法入口 |
|---|---|
| 修改页面、Hook 或宿主接线 | `uni-code-change`；React Native 实现细节查 `uni-rn-dev` |
| 排查账号切换后写回、H5 回包等故障 | `uni-debugging` |
| 审查页面或共享核心的接线差异 | `uni-code-review` |
| 补状态或宿主回归用例 | `uni-test-design` |
| 选择并运行本次平台验收检查 | `uni-verify-change` |
| 维护独立 RN 库的公开入口和包产物 | `uni-rn-library` |
