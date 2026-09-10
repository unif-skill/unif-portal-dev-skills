# Agent Skills 与 Agent Plugins 标准补齐

日期：2026-09-07。用户确认补齐标准插件清单、格式验证及规范说明。该工作扩充本地打包范围，不改变技能行为；原始[模型评测](https://github.com/unif-skill/unif-portal-dev-skills/blob/d8ab5d0c642ce3b5e21d2030c1cfb9727b5d8739/evals/architecture-design/runs/2026-09-07/RESULTS.md)和[接收复核](https://github.com/unif-skill/unif-portal-dev-skills/blob/d8ab5d0c642ce3b5e21d2030c1cfb9727b5d8739/evals/architecture-design/runs/2026-09-07/INTAKE.md)作为当时版本的记录保留。

## 规范依据与落地

| 依据 | 当前落实 |
|---|---|
| [Agent Skills Specification](https://agentskills.io/specification) | `skills/architecture-design/SKILL.md` 保持 YAML frontmatter 和 Markdown 正文；name 与目录一致，description 有明确适用范围，引用位于同目录的 references 中。 |
| [Agent Plugins Specification 1.0.0](https://agent-plugins.org/specification)，第 4—7 节 | 新增根 [plugin.json](../../plugin.json)，声明 canonical `$schema`、插件名及简短说明；技能位于 `skills/` 的直接子目录。 |
| [官方插件 JSON Schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json) | 使用官方下载内容验证根清单，未另写一份清单规则；规范正文与 Schema 冲突时以正文为准。 |
| [Agent Skills 参考库](https://github.com/agentskills/agentskills/tree/69ef37e9424c0a7ea9dd2293b559e43ec8176379/skills-ref) | 在临时虚拟环境运行 `skills-ref validate`，补齐先前仅运行 OpenAI quick_validate 的验证范围。 |

标准插件的最小完整分发内容如下；独立分发技能时仍可只复制整个 `skills/architecture-design/`。

```text
unif-portal-dev-skills/
├── plugin.json
└── skills/
    └── architecture-design/
        ├── SKILL.md
        └── references/
            ├── platform-architecture.md
            └── source.json
```

平台快照仍只由既有同步脚本维护。README、spec、评测与维护脚本可以保留在源码仓库，但不进入技能默认上下文。首版没有 MCP 或客户端扩展组件，因此不创建空组件配置。清单采用标准根路径，不依赖宿主专有清单或插件市场。

本次实际修改为：新增根清单和本记录，补充 README 的分发与校验说明，在原 spec 追加标准补齐范围。未修改技能正文、规范快照、来源记录、同步脚本、测试或既有评测材料。

## 首版格式验证复跑

从本仓库根目录执行。工具准备需要 Python 3.11+、Git 及访问官方源码和软件包源的网络。依赖只装入临时目录，不修改全局或项目依赖，也不会把插件安装到宿主。

先准备独立校验环境；各命令成功后再执行下一条：

```sh
PACKAGE_CHECK_TMP="$(mktemp -d)"
python3 -m venv "$PACKAGE_CHECK_TMP/venv"
"$PACKAGE_CHECK_TMP/venv/bin/python" -m pip install --disable-pip-version-check --no-cache-dir \
  'jsonschema==4.26.0' \
  'skills-ref @ git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref'
```

再下载已声明版本的官方 Schema 到该临时目录，核对本次使用的文件摘要并验证清单和技能。这里的网络读取是维护校验步骤；插件加载本身不依赖下载 Schema。

```sh
"$PACKAGE_CHECK_TMP/venv/bin/python" - "$PACKAGE_CHECK_TMP" <<'PY'
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from jsonschema import Draft202012Validator

schema_url = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
with urllib.request.urlopen(schema_url, timeout=20) as response:
    schema_bytes = response.read()
expected = "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883"
if hashlib.sha256(schema_bytes).hexdigest() != expected:
    raise SystemExit("官方 Schema 内容已变化，请核对规范差异后更新验证依据。")
(Path(sys.argv[1]) / "plugin.schema.json").write_bytes(schema_bytes)
schema = json.loads(schema_bytes)
Draft202012Validator.check_schema(schema)
manifest = json.loads(Path("plugin.json").read_text(encoding="utf-8"))
Draft202012Validator(schema).validate(manifest)
print("plugin.json：Agent Plugins 1.0.0 Schema 校验通过。")
PY
"$PACKAGE_CHECK_TMP/venv/bin/skills-ref" validate skills/architecture-design
```

该命令固定了两个直接工具的版本或源码提交；其传递依赖仍按上游声明解析，并非完整环境锁定。升级规范或工具时另记验证依据，不将新结果覆盖到本记录。

平台规范一致性及标准库测试继续使用根 README 的既有命令。前述格式检查不替代这两项，也不替代技能行为评测。

## 本次执行结果

本次环境：Python 3.14.7、jsonschema 4.26.0、skills-ref 0.1.0。参考库安装记录确认源码提交为 `69ef37e9424c0a7ea9dd2293b559e43ec8176379`。

| 检查 | 实际结果 |
|---|---|
| 根清单 | 官方 Draft 2020-12 Schema 自检及 plugin.json 验证均通过。 |
| 技能格式 | `skills-ref validate skills/architecture-design` 退出码 0，输出 `Valid skill`。 |
| 校验器反例检查 | 内存中构造的缺 `$schema`、缺 name、非法名称和未知顶层字段四种清单均不通过 Schema；未改写项目清单。未知字段属于 Schema 违规，实际客户端如何报告和忽略仍按规范第 5.2 节处理。 |
| 插件可搬移性 | 仅复制清单和完整技能目录到含空格的临时路径，共 4 个文件。清单及技能校验通过，按直接子目录规则静态枚举得到一个技能，从无关工作目录运行也通过。 |
| 包内引用 | 搬移后的所有文件及技能相对链接均解析到包内，目标存在；没有作者绝对路径或包外符号链接依赖。 |
| 同步脚本测试 | `python3 -m unittest discover -s tests -v`：4/4 通过。 |
| 平台规范 | 既有同步脚本 `--check` 退出码 0，规范快照与来源记录一致。 |
| 原始证据保护 | 技能、规范快照、脚本、测试和既有评测文件与本轮开始时一致；原 manifest 的 19 个评测文件哈希全部匹配。 |

本次根清单 SHA-256：`8d07f74e55a637a97f29638684b19cc2a8421119147dac2f836ec1e5b07cbf67`。官方 Schema 共 1,805 字节，其 SHA-256 已固定在上面的复跑命令中。

## 验证限制

上述结果证明当前四文件包满足本次使用的标准格式与包内引用要求。`skills-ref` 是官方参考校验库，定位为示范工具；它不证明技能的行为质量，也没有替代规范正文的全部语义检查。

静态枚举不等于真实宿主自动发现。尚未安装到任何宿主，未验证各客户端的安装、权限、加载与兼容行为。没有修改技能语义，因此未重跑模型样本；准确性增益、Token 节省、多模型稳定性和真实上下文压缩效果仍保持原记录的未验证结论。

本次未修改业务工程或人工维护规范源，未新增市场配置，未提交、推送或发布。
