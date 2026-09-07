# 完成巡检场景审查

依据随附规范审查以下设计。只输出必要调用关系、保留或调整理由和验证范围，不实现代码，不反问，尽量不超过 600 个汉字。以下均为该评测任务的设定，不证明任何真实仓库实现。

用户从客户搜索框明确选中客户后，要完成该客户的一项既有巡检。完成必须针对真实任务引用，不能创建任务。候选查询范围与分页规则暂未提供。

```ts
type CustomerRef = { customerId: string };
type InspectionRef = { inspectionId: string; customerId: string };
declare function readInspection(input: { ref: InspectionRef }): Promise<InspectionRef | null>;
declare function acquireVisitTask(input: { customer: CustomerRef }): Promise<InspectionRef>;
declare function closeInspection(input: { ref: InspectionRef; confirmation: string }): Promise<{ kind: 'ok' | 'rejected' | 'unconfirmed' }>;
```

第二个方法的职责为：查询同一客户可复用的巡检任务，完整查询确认没有且既有创建条件成立时创建；已有开始入口消费它。其参数与真实副作用以此说明为准。

草案建议完成入口调用第二个方法取得引用，再进入已有的确认和关闭场景。请判断是否成立。没有提供新的只读发现契约时，相关接口只作为候选，不声称当前工程已存在。
