# unif-portal-dev-skills

Unif 产品的研发技能集合，适用于 RN／原生鸿蒙 Portal 客户端、相关 Agent／Channel／CLI 及对应 @unif 库工程。仓库名中的 Portal 指产品；架构正文中的 Portal 指客户端职责边界。

[Unif 平台规范](plugins/unif-platform-rules/skills/unif-platform-rules/SKILL.md)提供本产品研发的公共规则。业务插件中的 11 个研发技能按平台与阶段选择。

| 目标 | 开发 | 测试 | 审查 |
|---|---|---|---|
| RN 客户端与库 | [unif-rn-dev](plugins/unif-react-native-skills/skills/unif-rn-dev/SKILL.md) | [unif-rn-test](plugins/unif-react-native-skills/skills/unif-rn-test/SKILL.md) | [unif-rn-review](plugins/unif-react-native-skills/skills/unif-rn-review/SKILL.md) |
| 原生鸿蒙客户端与 HAR | [unif-harmony-dev](plugins/unif-harmony-skills/skills/unif-harmony-dev/SKILL.md) | [unif-harmony-test](plugins/unif-harmony-skills/skills/unif-harmony-test/SKILL.md) | [unif-harmony-review](plugins/unif-harmony-skills/skills/unif-harmony-review/SKILL.md) |
| Python 后端 | [unif-python-dev](plugins/unif-python-skills/skills/unif-python-dev/SKILL.md) | [unif-python-test](plugins/unif-python-skills/skills/unif-python-test/SKILL.md) | [unif-python-review](plugins/unif-python-skills/skills/unif-python-review/SKILL.md) |

跨平台共用 [unif-architecture-design](plugins/unif-engineering-skills/skills/unif-architecture-design/SKILL.md) 处理职责、契约与状态设计，[unif-code-delivery](plugins/unif-engineering-skills/skills/unif-code-delivery/SKILL.md) 处理工程门禁、版本和授权交付。各阶段技能按职责引用相关公共主题。

## 与 Uni 技能的职责分工

| 规则对象 | 通用维护入口 | Unif 专项内容 |
|---|---|---|
| RN 源码与平台接入 | `uni-rn-dev` | Portal 目录、环境和状态采用、组件选型、H5 与业务契约 |
| RN 库工程与产物 | `uni-rn-library` | `@unif` 库职责、组织采用及真实业务消费者 |
| ArkTS／ArkUI 与原生接入 | `uni-harmony-dev` | Unif 原生目录、视觉要求、身份及跨能力交接 |
| HAR 工程与产物 | `uni-harmony-library` | `@unif/harmony-*` 库契约、同源资源与指定宿主验收 |
| 用例与覆盖率方法 | `uni-test-design` | 业务不变量、平台接线及实际验收对象 |

通用方法按场景引用技能名称，Unif 的开发、审查和测试入口共用所属规范资料。纯项目契约核对只读取专项内容；涉及平台实现或库工程时才组合通用技能。专项正文不复制通用方法，跨插件引用不依赖本机目录；缺少必要来源时保留具体缺项，不以复制旧规则或推测替代依据。

## 库插件

库能力技能共 11 个，各自随同名插件安装。Icons、Design、Chat、Camera、HMS Scan、Umeng、Logger 在同一入口内区分 RN 与原生鸿蒙；其余四项当前对应 RN 包。鸿蒙资料按实际库区分公开 API、目标契约与空 HAR，不因技能覆盖而声明功能已实现或已发布；开发、测试与审查仍按实际任务使用对应阶段技能。

| 技能 | 对应包与任务 |
|---|---|
| [unif-design](plugins/unif-design/skills/unif-design/SKILL.md) | @unif/react-native-design、@unif/harmony-design：基础组件、主题、字体和 UI 宿主 |
| [unif-chat](plugins/unif-chat/skills/unif-chat/SKILL.md) | @unif/react-native-chat、@unif/harmony-chat：消息、输入、附件和聊天组合 |
| [unif-camera](plugins/unif-camera/skills/unif-camera/SKILL.md) | @unif/react-native-camera、@unif/harmony-camera：拍照、录像、水印、取消与媒体交接 |
| [unif-hms-scan](plugins/unif-hms-scan/skills/unif-hms-scan/SKILL.md) | @unif/react-native-hms-scan、@unif/harmony-hms-scan：实时扫码、图片解码、权限和手电 |
| [unif-umeng](plugins/unif-umeng/skills/unif-umeng/SKILL.md) | @unif/react-native-umeng、@unif/harmony-umeng：初始化、统计、第三方分享与实例面板 |
| [unif-icons](plugins/unif-icons/skills/unif-icons/SKILL.md) | @unif/react-native-icons、@unif/harmony-icons：图标消费、SVG 源与生成 |
| [unif-amap](plugins/unif-amap/skills/unif-amap/SKILL.md) | @unif/react-native-amap：地图选点、定位、地点查询与高德唤起 |
| [unif-files](plugins/unif-files/skills/unif-files/SKILL.md) | @unif/react-native-files：文件操作、下载、生命周期与本地 HTTP 资源 |
| [unif-logger](plugins/unif-logger/skills/unif-logger/SKILL.md) | @unif/react-native-logger、@unif/harmony-logger：结构化日志、身份隔离、诊断快照与共享核心 |
| [unif-oss](plugins/unif-oss/skills/unif-oss/SKILL.md) | @unif/react-native-oss：临时凭证、上传、转存与源文件释放 |
| [unif-speech](plugins/unif-speech/skills/unif-speech/SKILL.md) | @unif/react-native-speech：音频采集、临时凭证、实时识别与语音输入 |

原生开发从 [unif-harmony-dev](plugins/unif-harmony-skills/skills/unif-harmony-dev/SKILL.md) 进入，按需取得 ArkTS 文件、状态、原生接入、UI、HAR 与验证规则。RN、鸿蒙应用／库分别组织，共享 TS 与资源必须具有同一来源及各目标验证。

鸿蒙库按已采用版本核对公开入口。目标契约和实现的版本差异见[鸿蒙库覆盖检查](evals/library-skills/harmony-library-cases.md)。

工程如何记录规范与契约入口，见[工程接入示例](docs/code-development-integration.md)。

RN 库的文档站和运行示例采用方式见 [RN 项目采用](plugins/unif-react-native-skills/skills/unif-rn-dev/references/rn/project.md)。

库能力入口指向所属库的公开文档、版本化 llms 索引、实际类型与必要维护资料。先核对采用版本，官网最新文档不代表已安装版本具备全部能力。跨库契约由规范仓维护，公开 API 与示例由库维护，技能维护任务指引和资料定位；不复制完整 API 或实时开发状态。

## 安装与使用

通过 Codex 市场安装。读取私有仓库需要相应权限和 Git 认证。

| 插件 | 所含技能 |
|---|---|
| `unif-platform-rules`（默认） | 跨插件共用的职责、场景、状态、交接与验证规则 |
| `unif-engineering-skills` | 架构设计、代码交付 |
| `unif-react-native-skills` | RN 开发、测试、审查 |
| `unif-harmony-skills` | 原生鸿蒙开发、测试、审查 |
| `unif-python-skills` | Python 开发、测试、审查 |

另从[库插件清单](#库插件)选择所需的库，例如 `unif-chat`、`unif-design`、`unif-camera`。每个库插件只包含自身技能与资料。

在 Codex 的“添加市场”中填写 [Git 仓库地址](https://github.com/unif-skill/unif-portal-dev-skills.git)，分支选 `main`。确认 `unif-platform-rules` 已安装并启用后，再选需要的业务插件。部分客户端仅显示默认安装策略；如果公共插件仍显示可安装，先在市场中安装它。

也可使用 Codex CLI 和 Python 3，从本仓的常驻克隆运行安装命令。未配置市场时，脚本将该克隆注册为本地市场；已有市场时沿用原配置。无参数时只装公共插件，以下示例安装 Chat 库插件并确保公共插件已安装。需要多个库时，依次列出插件名即可。

```sh
sh scripts/install-plugins.sh unif-chat
```

更新已配置的 Git 市场可运行 `codex plugin marketplace upgrade unif-portal-dev-skills`。安装后打开新会话，核对公共插件和所选业务插件的技能入口。

已安装旧整包 `unif-library-skills` 的用户，刷新市场后，先用上述命令安装所需的库插件，再移除旧整包，避免同名技能重复加载。

```sh
codex plugin remove unif-library-skills@unif-portal-dev-skills
```

已安装旧版 React Native 插件的用户，更新本地克隆或刷新 Git 市场后，运行以下命令迁移。Codex 会分别保留两个插件 ID，先移除旧插件可避免重复加载开发、测试和审查技能。

```sh
codex plugin remove unif-rn-skills@unif-portal-dev-skills
./scripts/install-plugins.sh unif-react-native-skills
```

### 使用

按目标工具的方式加载技能，并在任务中指定，例如：

```text
使用 unif-design 技能，按本项目采用的包版本检查主题与字体接入。
```

技能识别、调用语法和图标显示由目标工具决定。

## 使用与分发

每个市场条目直接安装对应的 `plugins/<插件名>/` 目录。在该目录的 `skills/<技能名>/` 下维护入口、资料和资产，修改后即可校验或安装。

## 规范来源

跨项目的工程方法由 Uni 技能维护。Unif 规范正文在 `unif-platform-architecture` 维护，同步时按以下归属直接写入插件。

| 插件 | 随包提供的规范 |
|---|---|
| 平台规范 | 多个插件实际共用的设计依据、系统职责、场景组合、状态归属、跨系统契约及验证原则。普通订单提交在公共契约中只保留专项文档入口。 |
| 工程 | 架构设计专用的智能体上下文、成本分析和领域文档规则；组织交付资料随交付技能。 |
| RN、鸿蒙、Python | 各自的 Unif 工程采用、模块契约与消费者验收。开发、测试和审查技能按需引用同一插件里的对应章节；通用技术方法由 Uni 技能维护。 |
| 库能力 | 库专用规范随对应的库技能。例如鸿蒙 Camera 的契约在 Camera 技能中维护。 |

维护者在规范源更新后运行下列命令。各技能的 `references/source.json` 记录它所承接章节的来源和摘要。只改手写技能时，直接校验仓库。安装用户使用已经随包提供的文件。

```sh
python scripts/sync_architecture.py --source /path/to/unif-platform-architecture
python scripts/sync_architecture.py --source /path/to/unif-platform-architecture --check
python scripts/validate_repository.py
```

Unif RN 库的组织约定及非敏感值由 unif-code-delivery 的[组织资产](plugins/unif-engineering-skills/skills/unif-code-delivery/assets/organization.json)维护，接入时复制到目标工程 `.github/organization.json`；GitHub 采用和发布说明随该技能分发。此资产不适用于原生鸿蒙或后端，密钥仍由平台管理。

## 版本与发布

全部 16 个插件与根清单使用统一版本，由根 `plugin.json` 锚定，Git tag 使用对应的 `vX.Y.Z`。常规发布允许 minor／patch，自动发布保持当前已发布的 major；清单改为另一 major 也会停止，须另行取得明确授权。

- `main` 的新提交通过完整校验后，CI 检查当前版本标签到本次已验证提交之间的提交标题：包含 `feat: ...`、`feat(scope): ...` 等 feat 类型时递增 minor 并将 patch 归零；其余递增 patch。提交正文提到 feat 不参与判断，`!` 标记不触发 major 升级。同一 major 内显式指定、尚未发布且不落后于已有标签的新版本继续直接使用。
- 准备步骤只修改根及市场中各插件 `plugin.json` 的版本字段，全部清单在同一个版本提交中原子写回，对候选包再次执行带 tag 的完整包校验，再创建版本提交并以普通快进推送写回 `main`。发布步骤为该提交创建 tag 和 GitHub Release，发布说明由 GitHub 生成；main、tag 和清单版本保持一致。
- 重跑同一次 main 推送可识别其版本提交，继续未完成的发布，不再次升版。已发布且 tag 指向同一提交时跳过；草稿、同名 tag 冲突或倒退版本均停止处理。远端 main 已有其他更新时旧运行停止发布；写回不强推，写请求失败不自动重试。
- PR、tag 推送和手动触发仅校验。CI 使用 `GITHUB_TOKEN` 写回版本和创建标签，不会递归触发新的 push 工作流；版本提交也带有 `[skip ci]`。发布依据为原提交的完整检查、候选版本包校验及最终提交核对。Codex 的安装更新另行执行。

## 验证

- [工程校验运行记录](https://github.com/unif-skill/unif-portal-dev-skills/actions/workflows/validate.yml) 在 PR、main 或 `v*` tag 推送及手动触发时运行脚本测试和分发包校验：检查统一版本、技能格式、各插件的唯一技能目录、本仓市场入口、隔离安装下的文档与图标引用、主题资料摘要与源行段覆盖。校验 job 不依赖本地评测运行产物，保持只读，不调用模型、改写仓库文件或自动提交；仅依赖校验成功的发布 job 获得版本写回、创建 tag 和 Release 的权限。
- 格式遵循 [Agent Skills](https://agentskills.io/specification) 与 [Agent Plugins 1.0.0](https://agent-plugins.org/specification)。校验使用仓内[插件 Schema](scripts/schemas/plugin.schema.json)与[固定依赖](scripts/requirements-ci.txt)，复跑命令见下文。
- 行为验证使用独立的[评测样本与判据](evals/architecture-design/README.md)，历史运行记录保留原文。鸿蒙开发、测试与审查的隐式加载见[自动触发题干](evals/independent-skills/harmony-trigger-cases.md)及[独立判据](evals/independent-skills/harmony-trigger-rubric.md)，覆盖实际任务和平台／阶段排除场景。
- RN 与 Python 六个阶段技能的[独立行为组](evals/independent-skills/rn-python-behavior-cases.md)和[自动触发组](evals/independent-skills/rn-python-trigger-cases.md)复用现行任务并核对实际读取；[判据](evals/independent-skills/rn-python-rubric.md)分别说明独立消费、阶段选择及排除边界。
- 架构、交付及六库能力的[九题独立行为组](evals/independent-skills/capability-behavior-cases.md)、[23 项自动触发场景](evals/independent-skills/capability-trigger-cases.md)与[专项判据](evals/independent-skills/capability-rubric.md)覆盖资料应用、组合与排除边界；库材料按固定 Git 修订和摘要组装，不复制 API 正文或原始运行日志。
- 脚本测试覆盖 16 个插件的分发目录、规范归属和组织资产。插件安装与主题可达性另在全新环境验证；使用、维护、组合与排除场景见[库能力评测](evals/library-skills/README.md)。AMap、Files、Logger、OSS、Speech 与鸿蒙 Logger 的定向题见[专项案例](evals/library-skills/additional-library-cases.md)，不改写原六库的冻结输入。每次库 API 或行为变化核对相关资料入口、示例和评测；模型行为、宿主加载与节省成本须由独立证据说明。

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
