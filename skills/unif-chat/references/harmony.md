# 原生鸿蒙 Chat

先核对 [harmony-chat README](https://github.com/unif-design/harmony-chat/blob/main/README.md)、[包清单](https://github.com/unif-design/harmony-chat/blob/main/library/oh-package.json5)及其 main 入口；再按需要读取[原生目标契约](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-chat.md)。本地按同一相对路径读取，具体接口采用实际修订，规划组件名不等于已有 ArkUI 导出。

若当前仅有空 HAR 或 `export {};`，说明对应能力仍缺实现；不提供假定可运行的 Composer、消息列表、OHPM 安装或接入示例。仅核查契约不授权恢复开发。存在真实实现时，核对公开入口、依赖和消费者后再使用。

## 目标职责

Chat 负责消息、列表、输入、附件及过程／来源／确认／反馈的显示与组合；应用持有会话、草稿、上传、采集、SSE、业务请求和结果。发送事件不自行清稿，停止按钮交付意图，附件展示不启动设备或删除文件。

原生 Design、Icons 与 Markdown 能力按真实可用实现和完整依赖核对。不能把 RN 渲染器当 ArkUI 默认依赖，也不能用纯文本演示代表 Markdown 已完成。组件的 Builder／控制器形态取原生公开类型，不照搬 ReactNode、Hook 或 ref。

焦点、测量、滚动和动画归组件；业务会话和附件事实归调用方。键盘、安全区与列表的实际区域分别处理，旧会话回调不覆盖新状态。销毁 UI 不等于取消已提交业务。

## 实施与验证

有授权时从所属仓库 AGENTS.md、README 与有效契约核对实现，验证真实基础组件与主聊天、嵌入输入等消费者。保留事件原对象、前插位置、末尾跟随、流式呈现及受控值。

源码／自动化、独立 HAR 宿主、设备键盘／长文／大字号／读屏和真实业务链分别记录。空骨架可构建不证明聊天组件可用，UI 示例不证明 Agent、上传或业务操作通过。
