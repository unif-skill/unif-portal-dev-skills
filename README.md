# unif-portal-dev-skills

Unif Portal 产品的研发技能集合，适用于客户端及相关 Agent、Channel、CLI 工程。仓库名中的 Portal 指产品；架构正文中的 Portal 指客户端职责边界。

当前提供[架构与模块设计技能](skills/architecture-design/SKILL.md)，用于研发设计与审查。职责与验收要求见 [spec](docs/specs/2026-09-07-architecture-design-skill.md)。

## 使用与分发

- 独立技能：分发完整的 `skills/architecture-design/`，保留相对引用。
- 标准插件：分发根 [plugin.json](plugin.json) 与完整的 `skills/` 目录。
- 使用时声明目标工程采用的架构规范及版本；未指定时使用包内快照。

README、docs、evals、同步脚本和测试用于仓库维护，不进入技能默认上下文。当前尚未安装到宿主或发布。

## 规范来源

先修改 `unif-platform-architecture/ARCHITECTURE.md`，再通过脚本生成技能内的[平台快照](skills/architecture-design/references/platform-architecture.md)和 source.json。脚本保留正文，仅将包外相对文档链接转为文字。

脚本只同步根规范，领域方法在对应模块契约中维护，由技能按需读取。`SKILL.md`、spec 和 evals 单独维护，不由脚本生成。实现后的类型、运行时校验和模型 Schema 从业务代码契约取得。

```sh
python3 scripts/sync_architecture.py --source /path/to/unif-platform-architecture/ARCHITECTURE.md
python3 scripts/sync_architecture.py --source /path/to/unif-platform-architecture/ARCHITECTURE.md --check
python3 -m unittest discover -s tests
```

`--check` 只比较规范源、快照和来源记录的一致性，不修改文件。

## 验证

- 格式遵循 [Agent Skills](https://agentskills.io/specification) 与 [Agent Plugins 1.0.0](https://agent-plugins.org/specification)。官方 Schema、`skills-ref validate` 的环境与复跑命令见[格式验证记录](docs/validation/2026-09-07-agent-standards.md)。
- 行为验证使用独立的[评测样本与判据](evals/architecture-design/README.md)，历史运行记录保留原文。

格式校验、模型评测和实际宿主加载分别验证。
