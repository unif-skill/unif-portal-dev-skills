# Unif 技能独立分发与 1.0.0 契约

以下记录 1.0.0 起各次分发调整。当前公共插件、五个业务插件及安装要求见[安装与使用](../../README.md#安装与使用)，现行规范归属见[规范来源](../../README.md#规范来源)。

## 目标与范围

保留现有 12 个技能名称，每个完整目录都能独立分发。执行本技能职责所需的规范、资源和工具随目录提供，不依赖兄弟技能、仓库根维护目录或作者安装缓存。工程的业务契约、采用版本和实际命令仍由目标工程提供。

本次完整目录结构和资料来源调整明确采用 `1.0.0`。本次授权包含源码、规范、配套文档与验证，不包含提交、推送、发布或安装。后续主版本变更仍需明确授权；自动版本只递增 patch，当前校验允许 0.x.x 与 1.x.x，拒绝 2.x.x 及以上。

## 资料归属

架构规范继续由 unif-platform-architecture 维护。根 scripts 将各阶段必需章节生成到所属技能 references，记录原始来源摘要、选取章节、原始行段和产物摘要；不得手工复制维护。完整源覆盖与明确选取范围分别校验，新源章节、重复或缺失章节、失效链接及越界路径必须报错。

code-development 的客户端专题分为 references/rn/ 与 references/harmony/；共同状态、契约与诊断放 references/common/。测试、审查和交付携带本阶段需要的共同及平台资料，按任务选读；跨技能选择只能用于独立任务或可选便利入口，不能成为本技能的运行前置。

根 scripts、tests、evals、docs 仅用于仓库维护。运行必需工具必须位于所属技能目录。所有技能提供 agents/openai.yaml，保留名称和已有图标、调用策略等元数据。

## Unif RN 库交付配置

code-delivery 自有 references/package-naming.md、github.md、publishing.md 和 assets/organization.json。组织资产仅适用于 Unif RN 库，不套用到 Harmony、后端或其他工程。接入时将资产复制为目标工程 `.github/organization.json`，按工程采用规则落实配置；后续工具只读取工程配置，不定位 Unif 安装目录。

资产使用 schemaVersion 1，owner 为 unif-design，namePattern 为 `^@unif/react-native-[a-z0-9]+(?:-[a-z0-9]+)*$`，pagesURL 为 `https://unif-design.github.io/{repo}/`，releaseAppId 为 3890760。repositorySettings 采用原组织标准中的仓库设置对象；security 为 codeqlDefaultSetup:not-configured、dependabotSecurityUpdates:disabled、privateVulnerabilityReporting:true。App ID 已由实际应用及规则集核对；本资产不包含私钥、访问令牌或其他凭据，密钥继续由平台管理。obsoleteFiles 仅列出原标准明确停用的 Dependabot 配置和两种自动合并 workflow 文件名；不将停用文件清理等同于远端安全更新开关。

## 验收

- 全部 12 个完整技能目录在无兄弟技能及根维护目录的隔离环境中通过格式、引用和生成资料校验，实际所需正文可达。
- RN／鸿蒙专题跨目录链接、源行段选取、增删迁移、重复生成和只读检查正确；来源、链接或路径检查失败时不部分覆盖既有资料，不穿过符号链接或路径边界。
- 组织资产在独立 code-delivery 中可取得，命名、Pages 与发布身份适用范围清楚，缺项及敏感字段被拒绝。
- 1.0.0 可校验与准备，后续 1.x patch 保持原自动规则；2.x、倒退标签、并发覆盖和无授权场景仍拒绝或保持只读。
- 格式、脚本测试、行为评测、安装及实际工程验收分别报告，不将维护验证当作部署或发布证据。

## 平台入口拆分补充（2026-10-31）

本补充在完整目录独立分发的基础上，将开发、测试和审查按真实平台职责拆开；版本保持 1.0.0。旧三个混合入口不保留别名或并存实现：

| 原入口 | 当前入口 |
|---|---|
| code-development | rn-development、harmony-development |
| code-testing | rn-testing、harmony-testing、backend-testing |
| code-review | rn-review、harmony-review、backend-review |

backend-development、architecture-design、code-delivery 和六个 unif-* 能力技能继续保留，合计 17 个。RN 的 iOS／Android 差异在相应 RN 技能内选读，不另设技能。

每个测试、审查和开发目录包含自身职责必需的共同与平台规范，不强制依赖其他阶段或 uni-skills 安装。RN 企业规则只维护 Unif 采用关系与契约，不复制通用 react-native-development。共同规范由原架构源同源生成，平台入口不引入第二份手工规范。

迁移覆盖当前工程指南、技能元数据、同步器映射、测试和现行评测入口。历史设计、计划、验证记录与冻结原始评测保留原文和时间语境，不作为当前入口列表。

补充验收：17 个完整目录可逐一隔离校验；各平台开发、测试、审查仅依赖本平台与共同规范源；全部 11 个生成资料集通过 --check，源章节、路径与原子失败保护仍有效；旧入口从分发目录和同步选项移除。脚本、资料消费、安装及实际工程验证分别报告。交付操作仍以当前任务的明确授权执行。

## 1.1.0 命名修订

技能目录、frontmatter name、默认提示词及同步 CLI 统一采用 README 中的 `unif-*` 名称；原 backend 系列改为 `unif-python-*`。规范源为 `PYTHON_DEVELOPMENT.md`，阶段资料为 `references/python/`。原 1.0.0 的独立分发、职责与验收要求继续有效；旧技能目录不再保留为别名。


## 五插件分发补充（2026-11-03）

根 `skills/` 仍是唯一技能源，22 个当前 `unif-*` 技能名称不变，其他 Agent Skills 客户端继续从根目录安装。Codex 沿用同一市场 `unif-portal-dev-skills`，市场仅引用五个插件根：

- `unif-engineering-skills`：架构设计与代码交付，共 2 个技能。
- React Native、原生鸿蒙和 Python 插件各含开发、测试与审查 3 个技能。现行插件 ID 见[安装清单](../../README.md#安装与使用)。
- `unif-library-skills`：全部 11 个库能力，双平台技能保持完整，不按平台复制或拆分。

`plugins/<插件 ID>/` 由 `scripts/sync_plugins.py` 从根清单、资产及所属技能完整生成。每包有自身清单、图标、技能正文、元数据、规范与资产，可脱离根维护脚本及兄弟插件安装。逐文件校验须核对完整副本，禁止符号链接或越界引用；未知目标文件先核对归属，不静默删除。根清单保留兼容入口，不再被市场引用。

五包及根兼容清单使用统一版本、同一个 Git tag 与 Release。发布准备和恢复只接受六份清单的版本字段变化，六份版本必须一致；其他字段、技能正文、市场拓扑或额外文件变化不能伪装为发布写回。minor／patch、主版本授权、main 已验证源提交、并发快进及发布恢复门禁保持有效。

验收分别核对五包市场映射、22 技能分组、整包隔离格式及资源引用、生成副本一致性、版本原子写回及恢复拒绝篡改。维护测试不替代模型行为、宿主发现、设备或真实工程验收。当时的旧整包停用及显式插件限定引用迁移见[该版 README](https://github.com/unif-skill/unif-portal-dev-skills/blob/2391a8a082bef64d5e302b8f448292eaa6020a91/README.md)；不得将分包视为新增外部运行依赖。
