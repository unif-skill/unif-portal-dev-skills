# unif-portal-dev-skills

Unif 产品的研发技能集合，适用于 RN／原生鸿蒙 Portal 客户端、相关 Agent／Channel／CLI 及对应 @unif 库工程。仓库名中的 Portal 指产品；架构正文中的 Portal 指客户端职责边界。

企业研发规范共 11 个入口，按目标平台与当前阶段选择：

| 目标 | 开发 | 测试 | 审查 |
|---|---|---|---|
| RN 客户端与库 | [unif-rn-dev](skills/unif-rn-dev/SKILL.md) | [unif-rn-test](skills/unif-rn-test/SKILL.md) | [unif-rn-review](skills/unif-rn-review/SKILL.md) |
| 原生鸿蒙客户端与 HAR | [unif-harmony-dev](skills/unif-harmony-dev/SKILL.md) | [unif-harmony-test](skills/unif-harmony-test/SKILL.md) | [unif-harmony-review](skills/unif-harmony-review/SKILL.md) |
| Python 后端 | [unif-python-dev](skills/unif-python-dev/SKILL.md) | [unif-python-test](skills/unif-python-test/SKILL.md) | [unif-python-review](skills/unif-python-review/SKILL.md) |

跨平台共用 [unif-architecture-design](skills/unif-architecture-design/SKILL.md) 处理职责、契约与状态设计，[unif-code-delivery](skills/unif-code-delivery/SKILL.md) 处理工程门禁、版本和授权交付。每个测试和审查技能都携带本阶段需要的规范，独立使用不要求安装开发技能。

库能力技能共 11 个。Icons、Design、Chat、Camera、HMS Scan、Umeng、Logger 在同一入口内区分 RN 与原生鸿蒙；其余四项当前对应 RN 包。鸿蒙资料按实际库区分公开 API、目标契约与空 HAR，不因技能覆盖而声明功能已实现或已发布；开发、测试与审查仍按实际任务使用对应阶段技能。

| 技能 | 对应包与任务 |
|---|---|
| [unif-design](skills/unif-design/SKILL.md) | @unif/react-native-design、@unif/harmony-design：基础组件、主题、字体和 UI 宿主 |
| [unif-chat](skills/unif-chat/SKILL.md) | @unif/react-native-chat、@unif/harmony-chat：消息、输入、附件和聊天组合 |
| [unif-camera](skills/unif-camera/SKILL.md) | @unif/react-native-camera、@unif/harmony-camera：拍照、录像、水印、取消与媒体交接 |
| [unif-hms-scan](skills/unif-hms-scan/SKILL.md) | @unif/react-native-hms-scan、@unif/harmony-hms-scan：实时扫码、图片解码、权限和手电 |
| [unif-umeng](skills/unif-umeng/SKILL.md) | @unif/react-native-umeng、@unif/harmony-umeng：初始化、统计、第三方分享与实例面板 |
| [unif-icons](skills/unif-icons/SKILL.md) | @unif/react-native-icons、@unif/harmony-icons：图标消费、SVG 源与生成 |
| [unif-amap](skills/unif-amap/SKILL.md) | @unif/react-native-amap：地图选点、定位、地点查询与高德唤起 |
| [unif-files](skills/unif-files/SKILL.md) | @unif/react-native-files：文件操作、下载、生命周期与本地 HTTP 资源 |
| [unif-logger](skills/unif-logger/SKILL.md) | @unif/react-native-logger、@unif/harmony-logger：结构化日志、身份隔离、诊断快照与共享核心 |
| [unif-oss](skills/unif-oss/SKILL.md) | @unif/react-native-oss：临时凭证、上传、转存与源文件释放 |
| [unif-speech](skills/unif-speech/SKILL.md) | @unif/react-native-speech：音频采集、临时凭证、实时识别与语音输入 |

原生开发从 unif-harmony-dev 的[鸿蒙适用范围](skills/unif-harmony-dev/references/harmony/scope.md)进入，按需取得 ArkTS 文件、状态、原生接入、UI、HAR 与验证规则。RN、鸿蒙应用／库分别组织，共享 TS 与资源必须具有同一来源及各目标验证。

鸿蒙库按已采用版本核对公开入口。目标契约和实现的版本差异见[鸿蒙库覆盖检查](evals/library-skills/harmony-library-cases.md)。

工程如何选择阶段与库技能，见[工程接入示例](docs/code-development-integration.md)。

RN 库的文档站和运行示例采用方式见 [RN 项目采用](skills/unif-rn-dev/references/rn/project.md)。

库能力入口指向所属库的公开文档、版本化 llms 索引、实际类型与必要维护资料。先核对采用版本，官网最新文档不代表已安装版本具备全部能力。跨库契约由规范仓维护，公开 API 与示例由库维护，技能维护任务指引和资料定位；不复制完整 API 或实时开发状态。

## 安装与使用

可通过 Vercel Skills 按名称安装单个完整技能，或在 Codex 市场按职责安装插件。从私有仓库获取文件需要仓库读取权限和 Git 认证。

### 使用 Vercel Skills

准备符合 [Skills CLI 要求](https://github.com/vercel-labs/skills#readme)的 Node.js（含 npm/npx）和 Git，在目标项目目录运行：

```sh
npx skills add unif-skill/unif-portal-dev-skills --skill unif-code-delivery
```

安装其他技能时，将 `--skill` 后的名称换成上表中的对应项。

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

在 Codex 的“添加市场”入口填写[仓库地址](https://github.com/unif-skill/unif-portal-dev-skills.git)，分支选择 `main`，不要使用 README 或技能子目录的链接。添加后按任务选择下表插件安装，全部安装包含 22 个技能，插件前缀按所选包显示。

| 插件 ID | 技能范围 |
|---|---|
| `unif-engineering-skills` | 架构设计、代码交付（2 个） |
| `unif-rn-skills` | RN 开发、测试、审查（3 个） |
| `unif-harmony-skills` | 原生鸿蒙开发、测试、审查（3 个） |
| `unif-python-skills` | Python 开发、测试、审查（3 个） |
| `unif-library-skills` | 全部 11 个库能力；双平台资料不拆分 |

也可使用 Codex CLI：

```sh
codex plugin marketplace add unif-skill/unif-portal-dev-skills --ref main
codex plugin add unif-engineering-skills@unif-portal-dev-skills
codex plugin add unif-rn-skills@unif-portal-dev-skills
codex plugin add unif-harmony-skills@unif-portal-dev-skills
codex plugin add unif-python-skills@unif-portal-dev-skills
codex plugin add unif-library-skills@unif-portal-dev-skills
```

界面与 CLI 任选一种添加方式。已添加的市场直接打开使用；刷新市场内容时运行 `codex plugin marketplace upgrade unif-portal-dev-skills`，无需重复添加。

仓库的 [marketplace.json](.agents/plugins/marketplace.json) 是市场入口，仅引用 `plugins/<插件 ID>/` 内的五个标准插件，各目录都有自己的 `plugin.json`、图标及完整技能资料；清单格式见 [Codex 插件管理文档](https://learn.chatgpt.com/zh-Hans/docs/enterprise/plugin-management#支持的格式)。

### 使用

按目标工具的方式加载技能，并在任务中指定，例如：

```text
使用 unif-design 技能，按本项目采用的包版本检查主题与字体接入。
```

技能识别、调用语法和图标显示由目标工具决定。

## 使用与分发

- 独立技能：分发对应的完整技能目录，保留相对引用。
- 标准插件：分发所选 `plugins/<插件 ID>/` 的完整目录。每包具有 `plugin.json`、`assets/`、自身完整 `skills/`，不依赖根维护脚本、其他插件或个人缓存。Codex 的插件展示配置在各清单的 `extensions.com.openai` 中。
- 根 `skills/` 是唯一技能源；修改根技能或架构同步后运行 `python scripts/sync_plugins.py`，再以 `--check` 核对。生成目录不手改；检测到未知文件或符号链接时停止，先核对归属。根 `plugin.json` 管理包元数据与统一版本，市场按五个插件分发。

README、docs、evals、同步脚本和测试供仓库维护使用。

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

五个插件与根清单使用统一版本，由根 `plugin.json` 锚定，Git tag 使用对应的 `vX.Y.Z`。常规发布允许 minor／patch，自动发布保持当前已发布的 major；清单改为另一 major 也会停止，须另行取得明确授权。

- `main` 的新提交通过完整校验后，CI 检查当前版本标签到本次已验证提交之间的提交标题：包含 `feat: ...`、`feat(scope): ...` 等 feat 类型时递增 minor 并将 patch 归零；其余递增 patch。提交正文提到 feat 不参与判断，`!` 标记不触发 major 升级。同一 major 内显式指定、尚未发布且不落后于已有标签的新版本继续直接使用。
- 准备步骤只修改根及市场五个 `plugin.json` 的版本字段，六份清单在同一个版本提交中原子写回，对候选包再次执行带 tag 的完整包校验，再创建版本提交并以普通快进推送写回 `main`。发布步骤为该提交创建 tag 和 GitHub Release，发布说明由 GitHub 生成；main、tag 和清单版本保持一致。
- 重跑同一次 main 推送可识别其版本提交，继续未完成的发布，不再次升版。已发布且 tag 指向同一提交时跳过；草稿、同名 tag 冲突或倒退版本均停止处理。远端 main 已有其他更新时旧运行停止发布；写回不强推，写请求失败不自动重试。
- PR、tag 推送和手动触发仅校验。CI 使用 `GITHUB_TOKEN` 写回版本和创建标签，不会递归触发新的 push 工作流；版本提交也带有 `[skip ci]`。发布依据为原提交的完整检查、候选版本包校验及最终提交核对。Codex 的安装更新另行执行。

## 验证

- [工程校验运行记录](https://github.com/unif-skill/unif-portal-dev-skills/actions/workflows/validate.yml) 在 PR、main 或 `v*` tag 推送及手动触发时运行脚本测试和分发包校验：检查统一版本、技能格式、五插件完整副本、本仓市场入口、隔离安装下的文档与图标引用、主题资料摘要与源行段覆盖。校验 job 不依赖本地评测运行产物，保持只读，不调用模型、改写仓库文件或自动提交；仅依赖校验成功的发布 job 获得版本写回、创建 tag 和 Release 的权限。
- 格式遵循 [Agent Skills](https://agentskills.io/specification) 与 [Agent Plugins 1.0.0](https://agent-plugins.org/specification)。校验使用仓内[插件 Schema](scripts/schemas/plugin.schema.json)与[固定依赖](scripts/requirements-ci.txt)，复跑命令见下文。
- 行为验证使用独立的[评测样本与判据](evals/architecture-design/README.md)，历史运行记录保留原文。鸿蒙开发、测试与审查的隐式加载见[自动触发题干](evals/independent-skills/harmony-trigger-cases.md)及[独立判据](evals/independent-skills/harmony-trigger-rubric.md)，覆盖实际任务和平台／阶段排除场景。
- RN 与 Python 六个阶段技能的[独立行为组](evals/independent-skills/rn-python-behavior-cases.md)和[自动触发组](evals/independent-skills/rn-python-trigger-cases.md)复用现行任务并核对实际读取；[判据](evals/independent-skills/rn-python-rubric.md)分别说明独立消费、阶段选择及排除边界。
- 架构、交付及六库能力的[九题独立行为组](evals/independent-skills/capability-behavior-cases.md)、[23 项自动触发场景](evals/independent-skills/capability-trigger-cases.md)与[专项判据](evals/independent-skills/capability-rubric.md)覆盖资料应用、组合与排除边界；库材料按固定 Git 修订和摘要组装，不复制 API 正文或原始运行日志。
- 全部 22 个技能的完整目录隔离分发、主题溯源及组织资产由脚本测试验证；使用、维护、组合与排除场景见[库能力评测](evals/library-skills/README.md)。AMap、Files、Logger、OSS、Speech 与鸿蒙 Logger 的定向题见[专项案例](evals/library-skills/additional-library-cases.md)，不改写原六库的冻结输入。每次库 API 或行为变化核对相关资料入口、示例和评测；模型行为、宿主加载与节省成本须由独立证据说明。

本地复现 CI（Python 3.12）：

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements-ci.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_repository.py
```

本地完成模型评测后，可加 `--include-evals` 校验运行目录中的 manifest 与原始文件摘要；默认分发包校验及 `validate.yml` 不读取这些目录。

校验工具版本与 Agent Skills 参考库提交固定在 [requirements-ci.txt](scripts/requirements-ci.txt)；[插件 Schema](scripts/schemas/plugin.schema.json) 是已声明版本的官方副本，校验时无需另行下载。CI 不读取开发机上的架构源，快照新鲜度仍在同步时通过上面的 `--check` 核对；模型行为通过下方独立工作流和本地专项评测取得证据。

### 查看评测报告

[工程校验](https://github.com/unif-skill/unif-portal-dev-skills/actions/workflows/validate.yml)检查仓库与插件。模型评测结果、运行入口及其证据范围见[行为评测说明](evals/behavior/README.md#运行与报告)。
