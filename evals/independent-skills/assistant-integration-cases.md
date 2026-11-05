# Python 智能体与能力目录独立行为题

仅提供题干与指定技能的完整目录，不提供判据、历史回答或其他工程。书面设计与实际工程运行分别记录。

## A：开发

Unif Agent 原有 api、core、db、services、schemas、utils。services/agent 负责小U路由、上下文与模型指令，services/execution 负责租约和任务状态，services/attachments 负责文件准备，services/clients/marketing.py 负责营销通信。现在按当前 Python 规范整理智能体自身模块及助手接入，只接入 Marketing，不预建未来助手。

Marketing 的订单、拜访和客户业务规则既被模型流程使用，也被普通 HTTP 入口使用。通用 memory 服务为模型和普通接口提供读写、权限与事务，另有智能体决定如何使用记忆的策略。请说明两工程的目录、依赖方向及必要迁移范围。当前 Python 工程没有 BasedPyright 配置，解释器和依赖已锁定。

## B：测试

团队把智能体自身指令与编排、Marketing 接入、领域校验分别归到新目录，普通接口继续调用既有能力，并认为导入检查通过就证明迁移完整。请按本技能设计验证，覆盖实际 Skill 和提示词装配、普通接口、通用 memory、输入来源、暂停恢复、取消、不同助手结果、身份、许可与用量。

可以使用第二个助手替身，但没有真实财务服务。新旧任务指令要求语义等价，Python 已采用工程 BasedPyright 配置。说明各层证据能证明什么。

## C：审查

某次目录整理提出以下做法。把所有名称含 AI 或 memory 的函数移入 agent，把普通接口调用的订单校验也搬到 agent/capabilities。营销适配器对唯一商品候选自动选中，Host 读取营销 action 判定拜访完成。公开 Schema 被复制为手写 DTO。为了通过类型检查，新增 ignore 并将未知外部对象直接 cast 成业务类型，却没有协议或运行校验依据。

请按本技能只读审查这些做法，区分智能体策略、独立领域能力、通用服务、协议校验、业务决策与类型检查依据。
