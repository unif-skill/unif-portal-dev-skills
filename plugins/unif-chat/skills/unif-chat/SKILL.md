---
name: unif-chat
description: 在查询、接入、维护或排查 @unif/react-native-chat 或 @unif/harmony-chat 的消息列表、输入、附件、流式展示、组件组合及鸿蒙目标契约时使用。
metadata:
  package: "@unif/react-native-chat"
  harmony_package: "@unif/harmony-chat"
---

# Unif Chat

原生鸿蒙的聊天组件、附件资源与输入宿主见[鸿蒙契约与实际库入口](references/harmony.md)。

## React Native

按锁定版本的包导出和公开类型核对下列资料。本地文档位于 `website/docs`，线上文档的构建版本见[官网索引](https://unif-design.github.io/react-native-chat/llms.txt)。

| 任务 | 使用资料 |
|---|---|
| 安装与公开组件 | [getting-started](https://unif-design.github.io/react-native-chat/md/getting-started.md)、[components/overview](https://unif-design.github.io/react-native-chat/md/components/overview.md) |
| 输入、语音操作与受控草稿 | [components/composer](https://unif-design.github.io/react-native-chat/md/components/composer.md) |
| 图片、文件、进度和重试展示 | [components/attachments](https://unif-design.github.io/react-native-chat/md/components/attachments.md)、[components/processing-progress](https://unif-design.github.io/react-native-chat/md/components/processing-progress.md) |
| 消息渲染与列表滚动 | [components/message](https://unif-design.github.io/react-native-chat/md/components/message.md)、[components/message-list](https://unif-design.github.io/react-native-chat/md/components/message-list.md) |
| 确认、建议、过程和来源 | [components/confirmation](https://unif-design.github.io/react-native-chat/md/components/confirmation.md)、[components/suggestions](https://unif-design.github.io/react-native-chat/md/components/suggestions.md)、[components/process](https://unif-design.github.io/react-native-chat/md/components/process.md)、[components/sources](https://unif-design.github.io/react-native-chat/md/components/sources.md) |
| 主聊天或抽屉组合 | [composition/main-chat](https://unif-design.github.io/react-native-chat/md/composition/main-chat.md)、[composition/drawer-input](https://unif-design.github.io/react-native-chat/md/composition/drawer-input.md) |

## RN 使用边界

接入或调整聊天界面时，先定位应用已有消息、草稿、附件和操作，核对当前公开组件、组合及真实消费者。已有独立组件或 Chat 组合能满足需求时直接使用；属于 Chat 展示或交互职责的缺口在授权内扩展所属能力，不复制库实现或为新入口另建同职责流程。组件展示状态并交回事件；会话事实、业务提交、附件准备、上传、采集及 Agent 通信（含 SSE）归应用，展示事件不代表业务成功。

主题、字体和基础控件使用 Design 的公开能力。拍照或扫码仅在需求涉及这些操作时查对应库的公开资料，已安装的库能力技能可按需使用；附件展示本身不启动设备、上传或临时文件清理流程。

源码维护与验证见[维护与组合验证](references/maintenance.md)。
