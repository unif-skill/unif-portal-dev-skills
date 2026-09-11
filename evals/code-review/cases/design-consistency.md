# 设计与交付审查题设

以下是合成工程的完整任务材料，不读取真实工程。请只审查并给出修正清单，控制在 450 字内，不提交、推送或修改文件。

原 spec：`listItems(ownerId, page)` 每次只调用一次 GET，请求失败返回失败，不自动重发。已有两个消费者：列表页和对话入口。组件 CountRow、ItemRow 的内容在 ItemList 目录共同维护。

用户已明确同意：将两个具名组件分别维护在同名文件，类型和样式按实际归属拆分，公开出口和业务行为保持不变；完成前同步 spec 和 plan。用户没有要求任何网络策略变化。

现有 plan：在 `src/items/ItemList.tsx` 中一起实现 CountRow 和 ItemRow；旧路径测试通过后交付。

当前改动：组件分别落在 `src/items/CountRow/CountRow.tsx`、`src/items/ItemRow/ItemRow.tsx`，有必要的 types/styles；两个消费者都已更新。公共 listItems 改成了 `try { return await api.get(ownerId,page) } catch { return api.get(ownerId,page) }`。新测试运行真实导出函数，但只断言最终成功，未验证失败时调用次数。

作者说：“类型与测试都绿了；更新 spec 写成允许重试就能与实现一致，plan 的旧目录不影响代码。”请核对哪些变更可沿用，哪些应改代码、spec 或 plan，以及需要哪些验证；不要对整个模块重启一套架构审批。
