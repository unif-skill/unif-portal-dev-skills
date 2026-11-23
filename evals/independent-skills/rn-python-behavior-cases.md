# RN 与 Python 独立行为题

本组分别检查RN 工程和 Python 服务两个技能能否结合公共规范处理题设。复用下表现行题目，不另维护一份相同正文；本文件供评测者组装输入，不整份交给被测上下文。判据见[RN 与 Python 评测判据](rn-python-rubric.md)。

| 编号 | 提供的完整技能目录 | 题干来源 | 二级标题 |
|---|---|---|---|
| B1 | `unif-rn-project` | [状态与记录归属](../architecture-design/cases/state-identity.md) | A：客户端恢复 |
| B2 | `unif-rn-project` | [独立消费题](cases.md) | A：unif-rn-project |
| B3 | `unif-rn-project` | [独立消费题](cases.md) | E：unif-rn-project |
| B4 | `unif-python-service` | [状态与记录归属](../architecture-design/cases/state-identity.md) | B：后端并发 |
| B5 | `unif-python-service` | [独立消费题](cases.md) | G：unif-python-service |
| B6 | `unif-python-service` | [独立消费题](cases.md) | H：unif-python-service |
| B7 | `unif-python-service` | [助手接入题](assistant-integration-cases.md) | A：开发 |
| B8 | `unif-python-service` | [助手接入题](assistant-integration-cases.md) | B：测试 |
| B9 | `unif-python-service` | [助手接入题](assistant-integration-cases.md) | C：审查 |

新增助手接入题另按[助手接入判据](assistant-integration-rubric.md)评阅。

## 组装与执行

1. 每题建立新的输入目录，放入该题业务技能、unif-platform-rules 的完整目录和 `TASK.md`。按插件中的相对路径附上目标入口直接链接的同包专项资料，保留技能原文与资产。其余业务技能、判据和其他运行结果留在输入之外。
2. 从表中来源截取对应二级标题之后、下一二级标题之前的正文，去掉首尾空行。将下方前缀、一个空行和该正文组成 `TASK.md`，末尾保留一个换行；不附加来源标题、其他题目或预期答案。
3. 在全新上下文发送下方执行请求，替换目录及技能名称两个参数。显式提供技能是本组条件，不能将其结果称为自动触发。

TASK.md 前缀：

```text
本次仅根据题设和提供的完整技能目录作答。各项事实是合成契约；不操作真实工程、服务、设备或业务记录。
```

执行请求：

```text
这是独立资料作答任务。只允许读取 <INPUT_DIR> 内的 TASK.md、<SKILL_NAME>、随题提供的同包专项资料和 unif-platform-rules 完整目录；不读取其他技能、记忆、父任务、其他工程、判据或历史回答，不联网、不委派、不写文件、不执行工程或真实业务。请先读 TASK.md，按题设及确有需要的技能资料直接作答，文末列实际读取文件全路径；缺失事实如实限定，不虚构运行。出现额度或积分警告立即停止并报告，不尝试其他调用途径。
```

来源题设中的实现、服务和测试事实仅在题内成立。具体工程或 SDK 未提供时应限制结论；书面方案、实际资料读取和真实工程运行分别记录，不把题设通过写成本轮实测。
