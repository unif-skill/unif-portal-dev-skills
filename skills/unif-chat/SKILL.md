---
name: unif-chat
description: 在使用、维护或排查 @unif/react-native-chat 的消息列表、输入区、附件、流式展示或聊天组件组合时使用。
metadata:
  package: "@unif/react-native-chat"
---

# Unif Chat

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-chat/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

## 按任务读取

本地使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读所需组件和组合单页，完整 API 从采用版本的公开类型取得。

| 任务 | 使用资料 |
|---|---|
| 安装与公开组件 | [getting-started](https://unif-design.github.io/react-native-chat/md/getting-started.md)、[components/overview](https://unif-design.github.io/react-native-chat/md/components/overview.md) |
| 输入、语音操作与受控草稿 | [components/composer](https://unif-design.github.io/react-native-chat/md/components/composer.md) |
| 图片、文件、进度和重试展示 | [components/attachments](https://unif-design.github.io/react-native-chat/md/components/attachments.md)、[components/processing-progress](https://unif-design.github.io/react-native-chat/md/components/processing-progress.md) |
| 消息渲染与列表滚动 | [components/message](https://unif-design.github.io/react-native-chat/md/components/message.md)、[components/message-list](https://unif-design.github.io/react-native-chat/md/components/message-list.md) |
| 确认、建议、过程和来源 | [components/confirmation](https://unif-design.github.io/react-native-chat/md/components/confirmation.md)、[components/suggestions](https://unif-design.github.io/react-native-chat/md/components/suggestions.md)、[components/process](https://unif-design.github.io/react-native-chat/md/components/process.md)、[components/sources](https://unif-design.github.io/react-native-chat/md/components/sources.md) |
| 主聊天或抽屉组合 | [composition/main-chat](https://unif-design.github.io/react-native-chat/md/composition/main-chat.md)、[composition/drawer-input](https://unif-design.github.io/react-native-chat/md/composition/drawer-input.md) |

## 使用边界

先确认应用已经持有的消息、草稿、附件和操作，再选择独立组件或已有 Chat 组合。组件展示外部状态并交回事件；业务提交、会话事实、上传、采集和 SSE 归应用对应能力。事件触发、动画结束或回调返回不能自行变成业务成功。

主题、字体和基础控件使用 Design 的公开能力。拍照或扫码仅在需求涉及这些操作时组合 unif-camera、unif-hms-scan；附件展示本身不启动设备、上传或临时文件清理流程。

## 维护与验证

需要源码维护或核对目标职责时读取[维护与契约](references/maintenance.md)，并按实际阶段取得 code-development、code-testing、code-review 或 code-delivery。单独安装本技能时可用工程指定的同一规范源补足维护规则；应用只消费组件不要求先具备架构仓。

验证真实组件、事件、受控数据及本次消费者。布局与交互变化在可比条件下检查主题、大字号、键盘、触达与可访问性；类型、Mock、Web、原生和设备证据分别报告。检查命令从当前 package.json/CI 取得，只查询接口或版本时不启动开发和发布。
