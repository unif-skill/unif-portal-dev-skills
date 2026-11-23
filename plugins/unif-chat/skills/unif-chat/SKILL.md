---
name: unif-chat
description: 组合消息列表、输入框和附件，处理滚动与流式展示等聊天界面问题。涵盖 @unif/react-native-chat 的组件用法与维护，以及原生鸿蒙 @unif/harmony-chat 的实际导出与目标契约。
metadata:
  package: "@unif/react-native-chat"
  harmony_package: "@unif/harmony-chat"
---

# Unif Chat

先确认聊天页实际使用的 Chat 版本，从该版本的公开组件选择消息、列表、输入或附件。RN 本地资料在 `website/docs`，完整单页与构建版本见官网索引。原生鸿蒙则查 HAR 的实际导出，入口为空时按目标契约说明实现缺口。[RN 组件与文档索引](https://unif-design.github.io/react-native-chat/llms.txt) · [鸿蒙组件与契约](references/harmony.md)

## 把组件接到现有聊天页

先看页面能否直接复用主聊天、抽屉输入或已有独立组件。主题和基础控件使用 Design。[主聊天组合](https://unif-design.github.io/react-native-chat/md/composition/main-chat.md) · [抽屉输入](https://unif-design.github.io/react-native-chat/md/composition/drawer-input.md)

- **草稿**由页面持有。组件显示输入并交回发送事件，页面按业务结果决定是否清空草稿。[Composer](https://unif-design.github.io/react-native-chat/md/components/composer.md)
- **附件**由应用准备、上传和释放。Chat 显示内容与进度，交回重试等操作。拍照、扫码由对应设备能力接手。[附件](https://unif-design.github.io/react-native-chat/md/components/attachments.md)
- **消息**由页面根据会话、业务回执和 Agent 或 SSE 返回的内容更新。Chat 呈现消息、过程与状态。

## 列表跳动或操作后界面未更新

列表跳动时，先查变化前的滚动位置，再查跟随策略、手动拖动和键盘造成的视口变化。只关心是否位于末尾，用 `onAtEndChange`。需要滚动偏移时，RN Chat 4.8.0 起的 `MessageList.onScroll` 会在更新内部位置和末尾状态后交付同一个原生事件。[消息列表](https://unif-design.github.io/react-native-chat/md/components/message-list.md)

操作后界面未更新时，顺着“组件收到的受控值 → 发出的事件 → 页面接收和采用的回执”核对。确有展示或交互缺口时，在所属 Chat 组件修复，用实际聊天页检查输入、附件点击、列表位置和键盘行为。[维护与组合验证](references/maintenance.md)
