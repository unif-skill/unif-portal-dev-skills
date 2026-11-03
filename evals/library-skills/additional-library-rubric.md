# 新增库人工判据

仅供评估者使用，不进入作答上下文。按[固定请求](additional-library-cases.md)和[源清单](additional-library-fixtures.json)核对实际读取、实现依据及消费者，而非按关键词或篇幅判定。没有执行设备或服务的题，不要求也不允许编造该层结果。

| 题目 | 必要依据与边界 |
|---|---|
| K1 AMap | 找到公开 MapPicker／openMapPicker、真实 example 与相关控制器。区分视野、查询中心、候选、选择和确认；取消／替换的迟到结果不得覆盖新调用。真实 SDK 补丁、权限、键盘与服务验证不能从 Mock 或纯 Web 推出，不为现有排障申请后台定位或更换供应商。 |
| K2 Files | 结合真实生命周期及 example 说明持有、独占读取、retire 和最终清理；不能把页面退出或 JS 上传取消视为读取结束。区分本地 HTTP 地址生成、文件存在及实际加载；保留根边界、符号链接限制、共享服务与 close 结果，不清空整个应用根目录。 |
| K3 RN Logger | 核对根入口、/files 与真实宿主。clear 保留活跃快照；身份切换／dispose 使未交付快照失效，已交付文件仍归接收方。等待实际读取结束后 release，不以分享面板打开代替；区分健康状态、部分清理和成功落盘。 |
| K4 OSS | 追踪真实 access→upload→源释放与 example；本地取消、原生终态、明确回执／未确认分别判断，凭证迟到响应不入失效实例。onRequestStarted 不是上传成功，onSourceReleased 才表示不再读取；不自动重传未确认对象，不删除调用方仍被读取的文件。 |
| K5 Speech | 核对真实权限／采集／会话／input 与 example。旧轮次不采用新回调，静默 context_ended 与卸载、原生 stop 收尾、词表／凭证等待及服务终态分别判断。transcript 不等于草稿，confirmed／unconfirmed、失败定稿与取消按实际契约采用；不以超时证明麦克风释放。 |
| K6 Harmony Logger | 从 library/oh-package.json5、Index.ts、Files.ts、logger-source.json 和 example 核实。文件入口为 /Files，需 context，不复制 RN /files 参数；采用明确 RN 修订，不假设最新 RN API 已同步。包声明、HAR 构建、设备行为与 OHPM 发布安装分层；纯消费不改生成核心或引入 RN 运行时。 |

若 example 只覆盖部分路径，应继续查真实公开实现，并说明未执行的组合；不得把示例片段描述成完整业务或设备验证。方案保持既有身份、权限、路径、取消、错误及资源保护，只有资料缺口限制需要它的判断。

发现题 1–6 分别对应 unif-amap、unif-files、unif-logger、unif-oss、unif-speech、unif-logger。实际实现排查可同时选相应平台阶段技能；纯接口与版本查询不因读源码自动变为开发或审查。7–9 不触发这些库能力技能，普通“日志、地图、语音”不能代替包身份与场景证据。

控制组已有正确判断记为保持。只完成静态目录、单次发现或资料引用，不报告自动触发率、模型增益、设备通过或 Token 节省；比较增益需另行冻结对照条件、独立重复和实际消费者验收。
