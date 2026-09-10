# unif-portal-dev-skills

Unif Portal 产品的研发技能集合，适用于客户端及相关 Agent、Channel、CLI 工程。仓库名中的 Portal 指产品；架构正文中的 Portal 指客户端职责边界。

当前提供：

- [architecture-design](skills/architecture-design/SKILL.md)：研发设计与审查，职责与验收见 [spec](docs/specs/2026-09-07-architecture-design-skill.md)。
- [portal-development](skills/portal-development/SKILL.md)：Portal 文件开发，目标工程调用方式见[接入说明](docs/portal-development-integration.md)。其 spec 由架构项目的 `docs/specs/2026-09-10-portal-development-skill.md` 维护。

## 安装与使用

技能采用 Agent Skills 格式，可安装到支持该格式的工具中。本仓库为私有仓库，需要本仓访问权限及可用的 Git 认证。

### 使用 Skills CLI

准备 Node.js（含 npm/npx）和 Git，在目标项目目录运行：

```sh
npx skills add unif-skill/unif-portal-dev-skills --skill architecture-design
```

安装 `portal-development` 时将 `--skill` 的值替换为该名称；手动分发时同样复制对应的完整技能目录。

按提示选择目标工具，例如 Claude Code、Cursor 或 Codex。默认安装到当前项目；需要用户级安装时，在命令后添加 `--global`。支持的工具、安装位置和认证方式见 [Skills CLI 文档](https://github.com/vercel-labs/skills#readme)。

通过 Skills CLI 安装的技能，可运行以下命令选择安装范围并更新：

```sh
npx skills update architecture-design
```

### 手动安装

也可直接克隆仓库：

```sh
git clone https://github.com/unif-skill/unif-portal-dev-skills.git
```

将 `skills/architecture-design/` 完整复制到目标工具支持的技能目录，保留 `SKILL.md`、`references/`、`agents/` 和 `assets/` 的相对位置；具体安装目录以目标工具文档为准。

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
使用 architecture-design 技能，依据本项目的架构规范审查这个模块的职责、接口交接和验证范围。
```

技能识别、调用语法和图标显示由目标工具决定。

## 使用与分发

- 独立技能：分发完整的 `skills/architecture-design/`，保留相对引用。
- 标准插件：分发根 [plugin.json](plugin.json)、`assets/` 与完整的 `skills/` 目录。插件使用 `assets/logo.png`，技能使用各自的 `assets/icon.png`；Codex 的插件展示配置放在标准清单的 `extensions.com.openai` 中。
- 使用时声明目标工程采用的架构规范及版本；未指定时使用包内快照。

README、docs、evals、同步脚本和测试用于仓库维护，不进入技能默认上下文。

`evals/*/cases/`、`rubric.md` 和评测方法纳入版本管理；`evals/*/runs/` 中的规范快照、原始输出、日志及结果记录仅在本地保留，由 `.gitignore` 排除。

## 规范来源

先修改 `unif-platform-architecture/ARCHITECTURE.md`，再通过脚本生成技能内的[平台主题资料](skills/architecture-design/SKILL.md#依据)和 source.json。脚本按完整章节拆分，保留源文及章节编号，将正文中的包外相对文档链接转为文字。source.json 记录源文件摘要、主题摘要及对应行段。

默认模式只同步 architecture-design 的根规范。领域方法在对应模块契约中维护，由技能按需读取。`SKILL.md`、spec 和 evals 单独维护，不由脚本生成。实现后的类型、运行时校验和模型 Schema 从业务代码契约取得。

```sh
python3 scripts/sync_architecture.py --source /path/to/unif-platform-architecture/ARCHITECTURE.md
python3 scripts/sync_architecture.py --source /path/to/unif-platform-architecture/ARCHITECTURE.md --check
python3 -m unittest discover -s tests
```

`--check` 只比较规范源、主题资料和来源记录的一致性，不修改文件。生成时要求源章节完整分配且不重复；章节新增或改名后需更新脚本中的主题映射。同步会清理旧的生成资料，手工文件不参与清理。

portal-development 使用同一脚本的独立模式，从规范目录读取 `PORTAL_DEVELOPMENT.md` 和 `PORTAL_STRUCTURE.md`，生成文件、UI、工具、依赖、目录及验证等主题。两个技能的入口按任务定位资料，完整目录仅在初始化或核对代码归属时读取。平台原则由 architecture-design 维护；业务结果、状态、确认及必要设计按职责调用，或读取目标工程指定的架构规范，不跨技能目录引用私有文件：

```sh
python3 scripts/sync_architecture.py --skill portal-development --source /path/to/unif-platform-architecture
python3 scripts/sync_architecture.py --skill portal-development --source /path/to/unif-platform-architecture --check
```

## 版本与发布

插件及所含技能共用根 `plugin.json` 的 `version`，采用 `X.Y.Z` 格式；Git tag 使用对应的 `vX.Y.Z`。

- 版本号显式修改并提交到 `main`；CI 不根据提交类型自动提升版本。
- `main` 推送通过完整校验后，发布 job 为尚未发布的 `0.x.x` 创建对应 tag 和 GitHub Release，标签固定到本次已验证的提交，发布说明由 GitHub 生成。已有 Release 时跳过；已有同名标签指向其他提交或存在草稿时停止，不覆盖。失败后可核对状态并重跑原工作流，写请求不自动重试。
- 发布 `1.0.0` 及更高版本前，每次都须由用户明确审核确认，包括这些版本的后续 minor 和 patch 升级；自动发布会跳过这些版本。审核后按人工流程创建同版本 tag，tag 校验通过后创建 Release。
- PR、tag 推送和手动触发仅校验，不自动发布。自动创建标签使用 `GITHUB_TOKEN`，不会再触发一轮 tag 工作流；其证据是同一流水线中先通过的完整校验，以及发布脚本对版本和标签提交的核对。Codex 的安装更新另行执行。

## 验证

- [GitHub Actions](.github/workflows/validate.yml) 在 PR、main 或 `v*` tag 推送及手动触发时运行脚本测试和分发包校验：检查版本、技能格式、标准插件清单、本仓市场入口、包内文档与图标引用、主题资料摘要与源行段覆盖。校验不依赖本地评测运行产物，保持只读，不调用模型、改写仓库文件或自动提交；仅依赖校验成功的发布 job 获得创建 tag 和 Release 的写权限。
- 格式遵循 [Agent Skills](https://agentskills.io/specification) 与 [Agent Plugins 1.0.0](https://agent-plugins.org/specification)。官方 Schema、`skills-ref validate` 的环境与复跑命令见[格式验证记录](docs/validation/2026-09-07-agent-standards.md)。
- 行为验证使用独立的[评测样本与判据](evals/architecture-design/README.md)，历史运行记录保留原文。

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
