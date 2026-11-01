# unif-portal-dev-skills

Unif 产品的研发技能集合，适用于 RN／原生鸿蒙 Portal 客户端、相关 Agent／Channel／CLI 及对应 @unif 库工程。仓库名中的 Portal 指产品；架构正文中的 Portal 指客户端职责边界。

本仓维护 Unif 企业规则及能力契约，可按完整插件或独立技能使用。通用工程规则从目标工程的采用来源取得；工程按实际安装技能的描述选择入口，不要求另装其他技能集合。

企业研发规范共 11 个入口，按目标平台与当前阶段选择：

| 目标 | 开发 | 测试 | 审查 |
|---|---|---|---|
| RN 客户端与库 | [unif-rn-dev](skills/unif-rn-dev/SKILL.md) | [unif-rn-test](skills/unif-rn-test/SKILL.md) | [unif-rn-review](skills/unif-rn-review/SKILL.md) |
| 原生鸿蒙客户端与 HAR | [unif-harmony-dev](skills/unif-harmony-dev/SKILL.md) | [unif-harmony-test](skills/unif-harmony-test/SKILL.md) | [unif-harmony-review](skills/unif-harmony-review/SKILL.md) |
| Python 后端 | [unif-python-dev](skills/unif-python-dev/SKILL.md) | [unif-python-test](skills/unif-python-test/SKILL.md) | [unif-python-review](skills/unif-python-review/SKILL.md) |

跨平台共用 [unif-architecture-design](skills/unif-architecture-design/SKILL.md) 处理职责、契约与状态设计，[unif-code-delivery](skills/unif-code-delivery/SKILL.md) 处理工程门禁、版本和授权交付。每个测试和审查技能都携带本阶段需要的规范，独立使用不要求安装开发技能。

库能力技能（当前六个入口只对应 RN 包；原生鸿蒙使用 unif-harmony-dev、unif-harmony-test、unif-harmony-review 及实际原生库文档）：

| 技能 | 对应包与任务 |
|---|---|
| [unif-design](skills/unif-design/SKILL.md) | @unif/react-native-design：基础组件、主题、字体和 UI 宿主 |
| [unif-chat](skills/unif-chat/SKILL.md) | @unif/react-native-chat：消息、输入、附件和聊天组合 |
| [unif-camera](skills/unif-camera/SKILL.md) | @unif/react-native-camera：拍照、录像、水印、取消与媒体交接 |
| [unif-hms-scan](skills/unif-hms-scan/SKILL.md) | @unif/react-native-hms-scan：实时扫码、图片解码、权限和手电 |
| [unif-umeng](skills/unif-umeng/SKILL.md) | @unif/react-native-umeng：初始化、统计、第三方分享与实例面板 |
| [unif-icons](skills/unif-icons/SKILL.md) | @unif/react-native-icons：图标消费、SVG 源与生成 |

原生开发从 unif-harmony-dev 的[鸿蒙适用范围](skills/unif-harmony-dev/references/harmony/scope.md)进入，按需取得 ArkTS 文件、状态、原生接入、UI、HAR 与验证规则。RN、鸿蒙应用／库分别组织，共享 TS 与资源必须具有同一来源及各目标验证。

工程调用方式见[接入说明](docs/code-development-integration.md)。本插件按当前任务提供企业规范入口；事实查询不因涉及源码就自动进入工程审查。进入实际工程阶段时取得对应依据，同一上下文已读且仍适用的内容直接复用；通用流程与企业规则用于同一次工作，不另开重复流程，也不强制依赖某个流程插件。

按任务组合研发阶段与库能力。接口查询可直接使用对应库能力技能；实际开发同时取得开发规则，测试、审查和交付按实际阶段取得。文档、文档站和运行示例按本库采用的规范与构建入口维护；Unif 约定从 unif-rn-dev 的 [RN 项目采用](skills/unif-rn-dev/references/rn/project.md)取得。应用消费与库源码维护分别选择资料；修改一个组件或 H5 消息不默认加载全部技能。

库能力入口指向所属库的公开文档、版本化 llms 索引、实际类型与必要维护资料。先核对采用版本，官网最新文档不代表已安装版本具备全部能力。跨库契约由规范仓维护，公开 API 与示例由库维护，技能维护任务指引和资料定位；不复制完整 API 或实时开发状态。

全部 17 个技能均可单独安装，只需对应完整目录，无需同时安装兄弟技能或整个插件。各技能携带职责范围内必需的规范、资产与元数据；架构正文从同一规范源按阶段生成，具体 API、业务契约及命令仍从目标工程取得。需要整套技能时也可使用兼容插件入口。

原 `code-development`、`code-testing`、`code-review` 已移除，按目标平台迁移到上表入口；更早的 `portal-development` 同样迁移至 `unif-rn-dev`。iOS 与 Android 仍由 RN 技能按实际影响选读，不再拆出平台技能。更新独立安装时替换原目录，避免旧入口继续被扫描；历史设计和冻结评测保留原名称与输入。

## 1.1.0 名称迁移

全部技能以 `unif-` 开头；原有六个 `unif-*` 库能力名称保持。Python 系列只改变技能与资料入口的命名，职责和行为契约不变。

| 原名称 | 当前名称 |
|---|---|
| `architecture-design` | `unif-architecture-design` |
| `code-delivery` | `unif-code-delivery` |
| `rn-development` | `unif-rn-dev` |
| `rn-testing` | `unif-rn-test` |
| `rn-review` | `unif-rn-review` |
| `harmony-development` | `unif-harmony-dev` |
| `harmony-testing` | `unif-harmony-test` |
| `harmony-review` | `unif-harmony-review` |
| `backend-development` | `unif-python-dev` |
| `backend-testing` | `unif-python-test` |
| `backend-review` | `unif-python-review` |

后端规范源改为 `PYTHON_DEVELOPMENT.md`，阶段资料使用 `references/python/`；生成器仅接受当前技能名称。旧名称不再分发，工程入口和同步命令按上表更新。独立安装时先取得完整新目录，再移除对应旧目录，避免重复发现；历史计划和冻结评测保留原命名语境。

## 安装与使用

技能采用 Agent Skills 格式，可安装到支持该格式的工具中。推荐使用 Vercel Skills 按需安装，下面以独立安装 `unif-code-delivery` 为例；完整插件仍可兼容分发。本仓库为私有仓库，从仓库获取文件需要访问权限及可用的 Git 认证；取得获授权分发的完整技能目录后，使用该技能不要求安装完整插件。

### 使用 Vercel Skills

准备符合 [Skills CLI 要求](https://github.com/vercel-labs/skills#readme)的 Node.js（含 npm/npx）和 Git，在目标项目目录运行：

```sh
npx skills add unif-skill/unif-portal-dev-skills --skill unif-code-delivery
```

安装其他技能时将 `--skill` 替换为上方列出的名称；命令只安装所选技能。测试、审查或交付技能自身包含必需规范，不需要额外安装开发或架构技能。

按提示选择目标工具，例如 Claude Code、Cursor 或 Codex。默认安装到当前项目；需要用户级安装时，在命令后添加 `--global`。支持的工具、安装位置和认证方式见 [Skills CLI 文档](https://github.com/vercel-labs/skills#readme)。

通过 Skills CLI 安装的技能，可运行以下命令选择安装范围并更新：

```sh
npx skills update unif-code-delivery
```

### 手动安装

也可直接克隆仓库：

```sh
git clone https://github.com/unif-skill/unif-portal-dev-skills.git
```

将所需的 `skills/<技能名>/` 完整复制到目标工具支持的技能目录，包括 `SKILL.md`、`references/`、`agents/` 及该目录已有的其他文件；不要只复制 `SKILL.md`。具体安装目录以目标工具文档为准。

更新时，在克隆的仓库中运行 `git pull --ff-only`，再替换已安装的完整技能目录。如有本地修改，先将旧目录备份到技能扫描目录之外。

### 插件市场（Codex，可选）

在 Codex 的“添加市场”入口填写[仓库地址](https://github.com/unif-skill/unif-portal-dev-skills.git)，分支选择 `main`，不要使用 README 或技能子目录的链接。添加后选择 `unif-portal-dev-skills` 安装。

也可使用 Codex CLI：

```sh
codex plugin marketplace add unif-skill/unif-portal-dev-skills --ref main
codex plugin add unif-portal-dev-skills@unif-portal-dev-skills
```

界面与 CLI 任选一种添加方式。已添加的市场直接打开使用；刷新市场内容时运行 `codex plugin marketplace upgrade unif-portal-dev-skills`，无需重复添加。

仓库的 [marketplace.json](.agents/plugins/marketplace.json) 是市场入口，引用根 `plugin.json` 所定义的标准插件；清单格式见 [Codex 插件管理文档](https://learn.chatgpt.com/zh-Hans/docs/enterprise/plugin-management#支持的格式)。

### 使用

按目标工具的方式加载技能，并在任务中指定，例如：

```text
使用 unif-design 技能，按本项目采用的包版本检查主题与字体接入。
```

技能识别、调用语法和图标显示由目标工具决定。

## 使用与分发

- 独立技能：分发对应的完整技能目录，保留相对引用。
- 标准插件：分发根 [plugin.json](plugin.json)、`assets/` 与完整的 `skills/` 目录。插件使用 `assets/logo.png`，已配置的技能图标随所属技能分发；Codex 的插件展示配置放在标准清单的 `extensions.com.openai` 中。
- 使用时声明目标工程采用的规范及版本；共同规则默认使用技能内同源快照，工程明确指定修订时采用该修订；实际业务契约、工具命令和配置以目标工程为准。

README、docs、evals、同步脚本和测试用于仓库维护，不进入技能默认上下文。

evals 中沿用的旧目录名是评测主题与历史档案位置，不是可安装技能名称；当前样本按平台入口执行，冻结 runs 不回写。

`evals/*/cases/`、`rubric.md` 和评测方法纳入版本管理；`evals/*/runs/` 中的规范快照、原始输出、日志及结果记录仅在本地保留，由 `.gitignore` 排除。

## 规范来源

RN 技能维护 Unif 的采用关系、职责和企业契约，不复制通用 uni-rn-dev 的组件、Hook 或平台实现规则，也不要求安装 uni-skills。通用工程规则由目标工程明确其有效来源。

共同规则由 unif-platform-architecture 的 ARCHITECTURE、PORTAL、HARMONY、PYTHON 规范及六库原生契约维护。先改规范源，再运行根同步器；各技能的 references/source.json 记录源摘要、章节原始行段与生成摘要。完整源逐章覆盖，阶段技能显式记录 selectedSections；缺失、重复或新增未登记章节都会失败。

RN、鸿蒙和后端各阶段目录分别携带自身平台主题，共同状态、契约和验证在各自 references/common/ 中。unif-rn-dev 的专项资料位于 references/rn/，unif-harmony-dev 的原生六库与工程专题位于 references/harmony/；unif-code-delivery 按交付对象携带所需验收主题。包外业务契约保留规范源相对路径作为定位线索，不假装已随包提供。

SKILL.md、手工任务指引、组织资产、spec 与 evals 单独维护。同步只清理已登记且带生成标记的旧文件，不覆盖手工文件或穿过符号链接。根工具不作为独立技能的运行依赖。

使用下方验证环境运行：

```sh
python scripts/sync_architecture.py --source /path/to/unif-platform-architecture/ARCHITECTURE.md
python scripts/sync_architecture.py --skill unif-rn-dev --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --skill unif-harmony-dev --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --skill unif-python-dev --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --skill unif-rn-test --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --skill unif-harmony-test --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --skill unif-python-test --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --skill unif-rn-review --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --skill unif-harmony-review --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --skill unif-python-review --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --skill unif-code-delivery --source /path/to/unif-platform-architecture
```

每条命令加 `--check` 只比较，不写文件。模型行为、安装生效与真实工程验证另行取得证据，不从来源一致性推断。

Unif RN 库的组织约定及非敏感值由 unif-code-delivery 的[组织资产](skills/unif-code-delivery/assets/organization.json)维护，接入时复制到目标工程 `.github/organization.json`；GitHub 采用和发布说明随该技能分发。此资产不适用于原生鸿蒙或后端，密钥仍由平台管理。

## 版本与发布

插件版本由根 `plugin.json` 维护，Git tag 使用对应的 `vX.Y.Z`。本次独立分发契约已明确授权采用 `1.0.0`，范围见[spec](docs/specs/2026-10-30-independent-skills-v1.md)。校验允许已授权的 `0.x.x` 与 `1.x.x`，继续拒绝 `2.x.x` 及以上；后续主版本变更仍需明确授权。

- `main` 的新提交通过完整校验后，CI 自动递增补丁号，例如 `1.0.0 → 1.0.1`；不根据提交类型自动升级 minor 或 major。日常修改无需手动改版本。若显式指定尚未发布且不落后于已有标签的已授权主版本内版本，则使用该版本。
- 准备步骤只修改 `plugin.json` 的版本字段，对候选包再次执行带 tag 的完整包校验，再创建版本提交并以普通快进推送写回 `main`。发布步骤为该提交创建 tag 和 GitHub Release，发布说明由 GitHub 生成；main、tag 和清单版本保持一致。
- 重跑同一次 main 推送可识别其版本提交，继续未完成的发布，不再次升版。已发布且 tag 指向同一提交时跳过；草稿、同名 tag 冲突或倒退版本均停止处理。远端 main 已有其他更新时旧运行停止发布；写回不强推，写请求失败不自动重试。
- PR、tag 推送和手动触发仅校验。CI 使用 `GITHUB_TOKEN` 写回版本和创建标签，不会递归触发新的 push 工作流；版本提交也带有 `[skip ci]`。发布依据为原提交的完整检查、候选版本包校验及最终提交核对。Codex 的安装更新另行执行。

## 验证

- [GitHub Actions](.github/workflows/validate.yml) 在 PR、main 或 `v*` tag 推送及手动触发时运行脚本测试和分发包校验：检查版本、技能格式、标准插件清单、本仓市场入口、包内文档与图标引用、主题资料摘要与源行段覆盖。校验 job 不依赖本地评测运行产物，保持只读，不调用模型、改写仓库文件或自动提交；仅依赖校验成功的发布 job 获得版本写回、创建 tag 和 Release 的权限。
- 格式遵循 [Agent Skills](https://agentskills.io/specification) 与 [Agent Plugins 1.0.0](https://agent-plugins.org/specification)。官方 Schema、`skills-ref validate` 的环境与复跑命令见[格式验证记录](docs/validation/2026-09-07-agent-standards.md)。
- 行为验证使用独立的[评测样本与判据](evals/architecture-design/README.md)，历史运行记录保留原文。鸿蒙开发、测试与审查的隐式加载见[自动触发题干](evals/independent-skills/harmony-trigger-cases.md)及[独立判据](evals/independent-skills/harmony-trigger-rubric.md)，覆盖实际任务和平台／阶段排除场景。
- RN 与 Python 六个阶段技能的[独立行为组](evals/independent-skills/rn-python-behavior-cases.md)和[自动触发组](evals/independent-skills/rn-python-trigger-cases.md)复用现行任务并核对实际读取；[判据](evals/independent-skills/rn-python-rubric.md)分别说明独立消费、阶段选择及排除边界。
- 架构、交付及六库能力的[九题独立行为组](evals/independent-skills/capability-behavior-cases.md)、[23 项自动触发场景](evals/independent-skills/capability-trigger-cases.md)与[专项判据](evals/independent-skills/capability-rubric.md)覆盖资料应用、组合与排除边界；库材料按固定 Git 修订和摘要组装，不复制 API 正文或原始运行日志。
- 全部 17 技能的完整目录隔离分发、主题溯源及组织资产由脚本测试验证；使用、维护、组合与排除场景见[库能力评测](evals/library-skills/README.md)。每次库 API 或行为变化核对相关资料入口、示例和评测；模型行为、宿主加载与节省成本须由独立证据说明。

本地复现 CI（Python 3.12）：

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements-ci.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_repository.py
```

本地完成模型评测后，可加 `--include-evals` 校验运行目录中的 manifest 与原始文件摘要；默认校验及 CI 不读取这些目录。

校验工具版本与 Agent Skills 参考库提交固定在 [requirements-ci.txt](scripts/requirements-ci.txt)；[插件 Schema](scripts/schemas/plugin.schema.json) 是已声明版本的官方副本，校验时无需另行下载。CI 不读取开发机上的架构源，快照新鲜度仍在同步时通过上面的 `--check` 核对；模型行为评测按规范或判断引导的实际变化另行执行。

格式校验、模型评测和实际宿主加载分别验证。
