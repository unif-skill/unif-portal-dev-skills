---
name: unif-chat
description: 在查询、接入、维护或排查 @unif/react-native-chat 或 @unif/harmony-chat 的消息列表、输入、附件、流式展示、组件组合及原生目标契约时使用。
metadata:
  package: "@unif/react-native-chat"
  harmony_package: "@unif/harmony-chat"
---

# Unif Chat

先确定 RN 或原生鸿蒙，再核对采用版本、公开入口与实际实现。目标契约、空 HAR、已实现 API 和已发布产物分别判断；不把 RN 接口改包名当作鸿蒙用法。

## 按平台读取

| 目标 | 入口 |
|---|---|
| React Native | 下方 RN 资料与当前包公开类型 |
| 原生鸿蒙 | [鸿蒙接入与契约](references/harmony.md)；先核对实际库，再按任务读取目标规范 |

独立消费只需本技能完整目录及对应库资料，不要求安装另一平台或其他技能。技能资料本身不授权恢复暂停的产品开发。

## RN 资料

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-chat/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

本地使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读所需组件和组合单页，完整 API 从采用版本的公开类型取得。

| 任务 | 使用资料 |
|---|---|
| 安装与公开组件 | [getting-started](https://unif-design.github.io/react-native-chat/md/getting-started.md)、[components/overview](https://unif-design.github.io/react-native-chat/md/components/overview.md) |
| 输入、语音操作与受控草稿 | [components/composer](https://unif-design.github.io/react-native-chat/md/components/composer.md) |
| 图片、文件、进度和重试展示 | [components/attachments](https://unif-design.github.io/react-native-chat/md/components/attachments.md)、[components/processing-progress](https://unif-design.github.io/react-native-chat/md/components/processing-progress.md) |
| 消息渲染与列表滚动 | [components/message](https://unif-design.github.io/react-native-chat/md/components/message.md)、[components/message-list](https://unif-design.github.io/react-native-chat/md/components/message-list.md) |
| 确认、建议、过程和来源 | [components/confirmation](https://unif-design.github.io/react-native-chat/md/components/confirmation.md)、[components/suggestions](https://unif-design.github.io/react-native-chat/md/components/suggestions.md)、[components/process](https://unif-design.github.io/react-native-chat/md/components/process.md)、[components/sources](https://unif-design.github.io/react-native-chat/md/components/sources.md) |
| 主聊天或抽屉组合 | [composition/main-chat](https://unif-design.github.io/react-native-chat/md/composition/main-chat.md)、[composition/drawer-input](https://unif-design.github.io/react-native-chat/md/composition/drawer-input.md) |

## RN 使用边界

先定位应用已有消息、草稿、附件和操作，按需选择独立组件或已有 Chat 组合。组件展示状态并交回事件；会话事实、业务提交、上传、采集和 SSE 归应用，展示事件不代表业务成功。

主题、字体和基础控件使用 Design 的公开能力。拍照或扫码仅在需求涉及这些操作时查对应库的公开资料，已安装的库能力技能可按需使用；附件展示本身不启动设备、上传或临时文件清理流程。

## RN 维护与验证

源码维护或核对目标职责时读取[维护与契约](references/maintenance.md)及库内 docs/DEVELOPMENT.md。应用只消费组件时使用当前公开资料，无需架构仓或其他技能。

验证真实组件、事件、受控数据及本次消费者。布局与交互变化在可比条件下检查主题、大字号、键盘、触达与可访问性；类型、Mock、Web、原生和设备证据分别报告。检查命令从当前 package.json/CI 取得，只查询接口或版本时不启动开发和发布。
