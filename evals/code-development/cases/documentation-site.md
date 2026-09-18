# 文档站与组件 Web 示例

每题使用独立上下文，不提供判据。发现阶段只提供五个阶段技能的描述与工程入口模板，正文和专题由被测者按任务选读，记录实际读取文件。以下均为合成任务，只产出实施与验收判断，不修改真实库；不把题设当成真实组件契约或已执行证据。

## A. 组件附带 Web 示例

请为 @unif/react-native-attachment 新增 AttachmentPreview 组件并提供可给库使用者看的 Web 示例。组件职责与 public types 已确认，当前只需决定实现与验收方式。仓库有 src/index.ts、src/AttachmentPreview/types.ts、example-web（Vite 页面，已有许多回调验证按钮）、docs/DEVELOPMENT.md；工程入口链接了并列的 Design、Camera、HMS Scan 库作为工程参考，还没有核对其网站。只给出你现在会采取的读取顺序、示例落点与页面结构、验证范围，不改文件，不假设看过未提供的源文件。

## B. 已有组件页质量与版本接线

完善一个 @unif 库已有的 Docusaurus 组件页：现在首屏是一张 900px 高占位图，下方铺了 25 个测试按钮和持续追加的 JSON 日志；已有真实组件导出、types、LiveDemo 容器及同站组件页面。开发者想直接复制另一库两年前的 RN Web shim、主题 Provider 与 fontScale 接线，类型检查和一张桌面截图过了就交付。本次只修这一组件页，给出具体页面组织、接线依据、同步与验收步骤，不改文件。

## C. 内部组件与原生能力反例

分别处理两个独立请求，只给出各自读取资料、修改与验证范围，不改文件。A：@unif Design 的一个 Button 只调整内部 disabled 样式，公开 API、行为和当前文档示例不变；不要改文档站。B：@unif Camera 只修 Android 相机资源释放，接口不变，无 Web 实现；这次不做网站。两库都有现有 website，但任务没有要求重建它们。
