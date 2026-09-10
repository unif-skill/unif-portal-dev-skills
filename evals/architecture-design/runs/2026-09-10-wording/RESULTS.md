# 两个技能入口的精简回归

本记录比较改写前后的 description，并验证精简正文仍能找到所需规则。规范快照、技能名称与调用策略没有变化；没有新增业务要求或复制平台原则。

## 材料与执行

输入、完整产出及摘要见 [manifest.json](manifest.json)。所有运行使用 `collaboration.spawn_agent`、`fork_turns: none`，不继承作者对话，不向被测上下文提供评分或其他输出。模型继承主任务默认设置，工具未提供精确版本、Token 和模型延迟。

- 描述回归：同一组 12 类请求，前后各五次独立运行，只给名称与 description，不给完整技能正文。
- 正文回归：三个已有场景各一次，提供精简后的适用技能和必要规范；独立安装场景只提供 portal-development。
- 主任务人工核对选择、理由及完整代码/设计产出，不按关键词出现次数评分。

## 结果

| 检查 | 实际结果 |
|---|---|
| 改写前描述 | 五次均按题设作出 12 项预设选择，60/60。 |
| 改写后描述 | 五次同样满足 12 项选择，60/60；没有将业务请求、后台私有函数修复、单纯测试或 PR 文案误归入两项技能。 |
| architecture-design 结果判断 | [response](outputs/response.md)满足既有 Q1—Q5：成功码与缺展示数据分开，保留列表及嵌套缺项，写入身份不补造，未知码/写超时不猜成功，其他领域不套营销成功码。 |
| portal-development 与共享原则 | [capability](outputs/capability.md)满足既有 D1—D4：角色文件与调用资源分开、SDK 正向注入；按需使用 architecture-design，原因列表缺项不被过滤，接口成功与写入输入分开，验证真实消费者和副作用。 |
| 独立安装与依据缺口 | [standalone](outputs/standalone.md)继续完成纯工具补测方案；缺少架构技能及工程规范时不自行实施业务事实迁移，明确缺口。 |

描述产出：[改写前 1](outputs/before-1.md)、[2](outputs/before-2.md)、[3](outputs/before-3.md)、[4](outputs/before-4.md)、[5](outputs/before-5.md)；[改写后 1](outputs/after-1.md)、[2](outputs/after-2.md)、[3](outputs/after-3.md)、[4](outputs/after-4.md)、[5](outputs/after-5.md)。

两份 SKILL.md 全文（含 frontmatter）的字符数：architecture-design 从 911 到 651，portal-development 从 907 到 694，总计减少约 26%。这是文本体积变化，不是模型 Token、延迟或准确率增益；原描述本身已经正确。本次仅说明在这些样本中未观察到识别退化。

格式与包内引用检查通过。模型产出为书面方案，未执行 TS/TSX 编译、SDK、Portal CI 或真实宿主的自动发现。正文每场景仅一次，也未覆盖所有历史行为样本；这些结果不构成全场景保证。规范、同步脚本、检查代码及既有冻结记录未因本次措辞调整而改变。
