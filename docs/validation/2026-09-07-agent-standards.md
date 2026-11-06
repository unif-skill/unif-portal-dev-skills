# Agent Skills 与 Agent Plugins 格式验证依据

本记录对应 2026-09-07 的单技能包，保留当时的标准采用与验证结论。当前目录、安装方式、依赖和校验命令见[仓库说明](../../README.md#验证)，不沿用首版的技能名称或临时安装步骤。

## 采用依据

- [Agent Skills Specification](https://agentskills.io/specification)：技能目录、frontmatter 与包内引用。
- [Agent Plugins Specification 1.0.0](https://agent-plugins.org/specification)及[官方 Schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json)：根插件清单。采用 Schema 的 SHA-256 为 `0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883`。
- [Agent Skills 参考库](https://github.com/agentskills/agentskills/tree/69ef37e9424c0a7ea9dd2293b559e43ec8176379/skills-ref)：使用固定提交执行 `skills-ref validate`。

## 验证结论与边界

当时的根清单、技能格式、包内引用和四文件隔离副本通过验证；缺 Schema、缺 name、非法名称和未知顶层字段四类反例均被拒绝。同步脚本 4 项测试及规范来源检查通过，既有 19 个评测文件的摘要保持一致。

当时环境为 Python 3.14.7、jsonschema 4.26.0、skills-ref 0.1.0。根清单 SHA-256 为 `8d07f74e55a637a97f29638684b19cc2a8421119147dac2f836ec1e5b07cbf67`。

上述结果只对应当时的格式与静态分发，不证明当前版本、宿主实际加载、模型效果或业务行为。原有[模型评测](https://github.com/unif-skill/unif-portal-dev-skills/blob/d8ab5d0c642ce3b5e21d2030c1cfb9727b5d8739/evals/architecture-design/runs/2026-09-07/RESULTS.md)和[接收复核](https://github.com/unif-skill/unif-portal-dev-skills/blob/d8ab5d0c642ce3b5e21d2030c1cfb9727b5d8739/evals/architecture-design/runs/2026-09-07/INTAKE.md)保留其原始范围。
