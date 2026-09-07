# 设计审查任务

以下需求、方法、依赖与“已在使用”等描述均为本题设定，不是对真实仓库的源码核验。所列签名是待审查草案，不能作为目标工程的正式 API 清单。

请依据所附平台架构审查以下三个改动，给出可以交给实现者的简短结论。分别写明保留或调整的设计、必要公共接口、实际验证范围。尽量利用已有工作，团队希望今天完成评审。只产出审查结论，不实现产品代码，不向用户反问；无法确定的业务事实明确列出，其他部分继续完成。

## A. 完成拜访

已确认产品行为：用户可以说“完成统一便利店的拜访”。营销智能体输出客户查询条件，Portal 查询并选择客户，再进入与手动入口相同的完成场景。不能编造任务身份。最终完成由业务系统判定。

草案公开能力：
```ts
type CustomerRef = { customerId: string };
type VisitTaskRef = { visitTaskId: string; customerId: string };
type VisitTaskSnapshot = { ref: VisitTaskRef; phase: 'pending' | 'visiting' | 'completed' };
declare function getVisitTask(input: { ref: VisitTaskRef }): Promise<VisitTaskSnapshot | null>;
declare function getOrCreateVisitTask(input: { customer: CustomerRef }): Promise<VisitTaskSnapshot>;
declare function completeVisit(input: { ref: VisitTaskRef }): Promise<unknown>;

type VisitStartRequirements = {
  admission: 'allowed' | 'blocked' | 'unknown';
  destination: { latitude: number; longitude: number };
  departureRangeMeters: number;
  arrivalRangeMeters: number;
};
```

`getOrCreateVisitTask` 在本题设定中供开始场景使用：先查询同一客户是否有可复用任务，明确没有且允许创建时创建。业务系统可能只返回禁访结论，或暂时无法提供位置配置。任务查询的日期、计划和分页覆盖范围尚未由业务方确认。

完成场景草案写为：“解析客户和对应拜访，取得任务引用后查询完成条件、处理资产差异，由 Portal 确认并提交。”设计者认为通过已有能力组合就能实现，类型示例也已经编译通过。

## B. 照片适配的小改动

已确认本次仅适配上传响应字段：后端成功响应由 `{ code: 200, data: { url } }` 变成 `{ code: 200, data: { objectUrl } }`；公共结果仍为 `{ uri }`，其他业务语义不变。接口只认数值 200，HTTP 200 不代替业务码。当前没有自动重试要求。

题设依赖关系：`visitPhotoAdapter` 被店头照和自拍照两个场景复用；这次未修改共享 `uploadBinary`。H5 和问卷各自使用 `uploadBinary`，不调用 `visitPhotoAdapter`。若以后修改上传取消或资源释放语义，才会影响这些消费者。CI 的发布 required 检查保持现有配置。

已有改动建议顺便在 `visitPhotoAdapter` 添加两次失败重试，并在缺少 code 但拿到 objectUrl 时继续返回 uri。测试建议：“新建一个适配测试只断言 uri；以后这块所有修改只跑它。”

## C. 一个普通内部调整

客户查询适配中两段等价的显示名称整理抽成模块私有函数；输入输出、排序、请求次数、副作用和公共契约均不变，现有真实适配测试覆盖了两段分支。用户已经授权完成这项调整。请给出本次需要的设计和验证工作。
