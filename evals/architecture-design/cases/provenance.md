# 两个独立项目的设计交接

请依据随附平台规范，分别给这两个项目写可交给实现者的简短结论：公开能力与命名、实际调用关系、尚缺依据和必要验证。只做设计，不改业务代码，不反问；全文尽量不超过 900 个汉字，接口片段可以简写。

## 项目甲：已有正式契约

目标模块已经评审确认以下公开契约及名称，当前只需要把一个新的聊天入口接进既有完成场景，公开语义不变：

```ts
type TaskRef = { taskId: string; customerId: string };
type Result<T> = { kind: 'ok'; value: T } | { kind: 'unavailable' };
declare function findExistingVisitTasks(input: { customerId: string }): Promise<Result<{ refs: TaskRef[]; complete: boolean }>>;
declare function getOrCreateVisitTask(input: { customerId: string }): Promise<Result<TaskRef>>;
declare function completeVisit(input: { ref: TaskRef; confirmation: string }): Promise<Result<{ completed: true }>>;
```

第一个函数只读，已有客户到任务的定位能力；第二个函数供开始场景使用，完整查询确认不存在且满足已有创建条件时可能创建。完成场景已有定位、必要选择、确认与提交链路。新聊天入口取得客户引用后应达到相同完成目标。以上是本题给出的目标正式契约；部署与源码未提供。

同事带来的上一轮评测摘录写着：“需要新增 findExistingVisitTasks 补齐只读交接；acquireVisitTask 可能创建；completeVisit 返回 unknown，需要重写结果契约。”该摘录来自另一个待审查样本。另一建议认为名字在评测出现过就不应再作为正式名称，主张将所有公开名称更换一遍。今天只完成本次接线设计。

## 项目乙：新模块，尚无公开 API 契约

这是另一个独立仓库的售后工单详情页。页面已经持有业务系统返回的明确工单引用。已确认需求是用户填写关闭说明，在页面确认后提交关闭；后端最终判断是否允许关闭。只规划必要模块边界。没有提供目标模块的现有函数清单、原始关闭接口字段和码表，不能据此声称某个函数已经存在。下一步按职责补齐设计候选与所缺依据，其他项目的资料不是本项目的契约。
