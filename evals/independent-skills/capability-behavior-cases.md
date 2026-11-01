# 架构、交付与六库能力独立行为题

本组检查八项技能能否从自身完整目录取得规则并应用到任务，共九题，其中交付分为流程边界与组织资产两题。本文件供评测者组装输入，不整份提供给作答者；判据见[专项判据](capability-rubric.md)。

| 编号 | 提供的完整技能目录 | 题干来源 | 截取范围 | 源材料 |
|---|---|---|---|---|
| B1 | `unif-architecture-design` | [架构 review](../architecture-design/cases/review.md) | 全文 | 无 |
| B2 | `unif-code-delivery` | [交付范围](../code-delivery/cases/delivery-stages.md) | 全文 | 无 |
| B3 | `unif-code-delivery` | [独立消费](cases.md) | C：unif-code-delivery 的二级标题正文 | 无 |
| B4 | `unif-design` | [库能力请求](../library-skills/cases.md) | A 项的请求文本 | `design` |
| B5 | `unif-chat` | [库能力请求](../library-skills/cases.md) | B 项的请求文本 | `chat` |
| B6 | `unif-icons` | [库能力请求](../library-skills/cases.md) | C 项的请求文本 | `icons` |
| B7 | `unif-camera` | [库能力请求](../library-skills/cases.md) | D 项的请求文本 | `camera` |
| B8 | `unif-hms-scan` | [库能力请求](../library-skills/cases.md) | E 项的请求文本 | `hms-scan` |
| B9 | `unif-umeng` | [库能力请求](../library-skills/cases.md) | F 项的请求文本 | `umeng` |

## 输入组装

每题新建目录，包含对应技能的完整目录与 `TASK.md`；B4–B9 再放入本题源材料，取得方式见[材料组装](capability-trigger-cases.md#材料组装)。不放兄弟技能、判据或历史结果。保留技能现有引用、元数据及资产，不修改技能正文。

`TASK.md` 按以下顺序拼接，部分之间保留一个空行，末尾保留一个换行：

1. 下方固定前缀。
2. 按上表取得题干，去掉首尾空行。B1/B2 保留全文标题；B3 不含二级标题及后续题目；B4–B9 去掉 `- A：` 等列表标记，仅保留请求。
3. B4–B9 附加下方资料说明，替换来源清单中的目录、版本和修订；B1–B3 不附加。

固定前缀：

```text
只根据题设及本次材料作书面判断，不修改工程、安装、联网、提交、发布、调用真实服务或操作设备。
```

资料说明：

```text
本题采用 project/<LIBRARY_DIRECTORY> 的公开源码和文档快照，版本 <VERSION>，修订 <COMMIT>。素材保留 package.json、公开源码及 website/docs，不包含原生运行环境或完整业务应用；路径按该库根目录解释，未包含的依赖事实应明确限定。只读取本题相关文件，不把提供的全部源码预先读入。
```

## 执行请求

每题使用全新上下文，替换输入目录及技能名称，发送以下请求：

```text
这是独立资料作答任务。只允许读取 <INPUT_DIR> 内的 TASK.md、<SKILL_NAME> 完整目录及已提供的 project 素材。允许 cat、sed、nl、rg 等枚举和读取命令；不读取其他技能、记忆、父任务、其他工程、判据或历史回答，不联网、不委派、不写文件、不运行工程或真实业务。先读 TASK.md，按题设与必要资料直接作答，文末列实际读取文件全路径；缺失事实如实限定，不虚构运行。出现额度或积分警告立即停止并报告，不尝试其他调用途径。
```

这是显式提供技能的资料应用测试，不是自动触发。题设中的业务、Git 状态或 SDK 条件不作为真实工程已经验证的证据。外部源码快照与任务版本固定，缺少原生实现、消费应用或运行环境时准确限定结论；只提出验证方法不等于执行了验证。
