# 原生六库规范与技能续作验证

日期：2026-10-27。当前授权仅为规范／契约资料、技能路由、生成与验证。鸿蒙产品开发暂缓；本任务不创建或实现库、应用及原生示例，完成后也不自动进入 Icons／Design 开发。

## 采用文件与身份

延续规范工作区 `unif-platform-architecture-harmony-foundation`（`codex/harmony-foundation`，HEAD `4cf9e0521447d25875b73ab5f6a20fd09fbdc7f6`）及技能工作区 `unif-portal-dev-skills-harmony-foundation`（同名分支，HEAD `45031095708ea614039e3370bafb04bbc4e59da8`）中的未提交候选，未覆盖原有修改。

| 资料 | 本次可采用内容 |
|---|---|
| 规范源 `HARMONY_DEVELOPMENT.md` | 应用消费／HAR 维护／共享核心的资料选择、六库入口、高德／友盟提供方、外部技能边界 |
| 规范源 `HARMONY_STRUCTURE.md` | API 26 玻璃的实际载体、支持区域、宿主配置及分端验收 |
| 规范源 `libraries/harmony-icons.md` | SVG／命名清单同源生成、显式颜色尺寸、Design 消费及无障碍 |
| 规范源 `libraries/harmony-design.md` | 基础数据与平台样式分离、字体单次缩放、受控组件、玻璃与确认／提示宿主 |
| 规范源 `libraries/harmony-chat.md` | 消息、输入、附件、过程呈现，应用草稿和业务状态边界 |
| 规范源 `libraries/harmony-camera.md` | 拍摄／预览选用、clear／retain、新旧调用、权限及交付后文件责任 |
| 规范源 `libraries/harmony-hms-scan.md` | 实时／图片解码、真实手电、人工选用、关闭时读取及借用释放 |
| 规范源 `libraries/harmony-umeng.md` | 同意后初始化、统计、实例面板、真实渠道回执与未知结果 |
| 技能 `skills/code-development/SKILL.md` | 共用阶段入口中新增六库原生资料路由；原有七个鸿蒙通则继续使用 |
| 技能 `skills/code-development/references/harmony-*.md` | 共 13 个专题，全部由规范源生成；不新增平行阶段或原生能力技能 |

六库规范都区分目标语义与已实现 API。Icons／Design 的职责、同源资源、公开出口与验收依据已可供后续获授权的实施采用；具体 ArkUI 导出仍需真实库编译和消费者验证。其他四库同时具备规范，并非已经完成库实现。

候选指纹见[文件摘要](https://github.com/unif-skill/unif-portal-dev-skills/blob/2391a8a082bef64d5e302b8f448292eaa6020a91/docs/validation/2026-10-27-harmony-library-foundation.json)。清单版本与当前安装插件均仍是 `0.3.19`；版本号相同不代表安装缓存包含本候选。未手改缓存，也未修改外部鸿蒙技能或工程采用记录。

本记录固定的是发布前候选。后续发布接入见[交付依据](2026-10-27-harmony-release.md)；历史清单不用于核对合入后或发布安装后的内容。

采用清单覆盖规范及直接行为对照、完整技能目录、清单／生成器／同步测试和相关说明／样本，共 106 个文件。JSON 文件 SHA-256：`e3e7cac262a442cbf93a680fed4591dc9c23ff189abd9dbdcb8ac8bf8f167e6b`。本说明及本地运行档案不纳入该清单，避免自引用；运行档案另有 manifest。书面候选冻结之后只补齐状态、证据和采用说明，六库规范与技能正文没有继续改变。

## 依据核查

- 交接的 [P0 记录](2026-10-27-harmony-foundation.md)与旧摘要共 76 文件，本次修改前全部匹配；旧清单 SHA-256 为 `bd8f715ee9bb96b079347d2b551081d9822fd6be59a2333e05712c5297a91da2`。旧摘要保留，不能用来核对六库续作后的当前内容。
- 本次阅读 RN 六库契约及 Design 字体／宿主等直接依赖，并核对 Icons 的默认 24／黑色／源描边、Design `tokens.ts` 的 RN 与缩放导入。没有把 RN 类型或示例声明为鸿蒙签名。
- [华为开启沉浸光感](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/arkts-immersive-light-sense-enable)及[简介](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-immersive-light-sense-overview)支持目标版本、组件区域和系统条件的规范；本机 SDK 元数据为 `26.0.0.105`，`@ohos.arkui.uiMaterial.d.ts` 存在 `getMaterialInfo`、`getGlobalMaterialLevel`、`isImmersiveMaterialSupported` 的 API 26 声明。声明核查不证明设备效果。外部知识检索未找到 API 26 光感的直接材料，未以近似结果替代。
- [友盟鸿蒙 U-Share 概述](https://devs.umeng.com/docs/128606/detail/2938160)核实了 common／analytics／share 的配套要求；[高德鸿蒙 SDK](https://lbs.amap.com/api/harmonyosnext-map3d-sdk/summary)作为地图提供方资料入口。未据概述推断全部渠道、具体 SDK 版本或 API 26 运行已通过。

## 本次验证

使用已有 Python 3.12.14 验证环境及仓库固定依赖（jsonschema 4.26.0、markdown-it-py 4.0.0、PyYAML 6.0.3、skills-ref 0.1.0），未新增依赖或改变发布配置。

| 检查 | 结果及范围 |
|---|---|
| 修改前完整回归 | 本次重新运行 81 项通过；不是复用历史通过数 |
| 新增来源回归 RED | 23 项同步测试出现 21 个子用例断言失败，原因是六库尚未纳入生成、缺源及漂移检测 |
| 子目录链接 RED | 加入六库映射后只剩 1 项失败：未打包 RN 契约路径丢失 `libraries/` 位置 |
| 修复后定向回归 | 23 项通过；六库源完整覆盖、缺任一源不写、各源／产物漂移只读检测和跨目录链接 |
| 完整回归 | 82 项通过，含六个 RN 能力技能独立分发回归 |
| 分发格式 | 12 个技能通过；六个 RN 能力目录与交接摘要一致 |
| 本地评测档案 | `validate_repository.py --include-evals` 通过：3 份评测清单、1493 个冻结文件；本轮清单覆盖其中 514 个文件 |
| 来源同步 | 架构、客户端、后端三个 `--check` 均通过；客户端从 10 份源生成，转写规则升级为 v4 |
| 文档与可移位读取 | 9 份源文档、45 个本地链接／锚点通过；独立复制 code-development 后包内引用与来源校验通过；相关差异格式检查通过 |

最终交付时再次核对采用清单中的 106 文件全部匹配，并检查 7 份说明／评测文档的本地引用。最终报告收尾没有修改已经通过回归的代码或六库规范正文。

生成器只扩展现有映射，并将嵌套源中未打包的引用规范化到规范根目录；保留查询及锚点语义、既有完整章节与路径保护。未手改生成专题。其他两项同步只因转写版本元数据一并重新生成，不增加后端职责。

主要复跑命令：在技能工作区使用上述环境运行 `python -m unittest discover -s tests -v`、`python scripts/validate_repository.py`；同步使用 `python scripts/sync_architecture.py --skill code-development --source <规范根> --check`，架构使用 `--source <规范根>/ARCHITECTURE.md`，后端使用 `--skill backend-development`。

## 书面平台路由样本

[固定六例](../../evals/code-development/harmony-library-cases.md)与[独立判据](../../evals/code-development/harmony-library-rubric.md)覆盖 Icons、Design、拍照选用、图片借用、友盟／高德和 Chat／共享 TS／RN 局部任务。基线与候选使用不同的隔离上下文及冻结资料；每个上下文顺序回答同组六例，并非每例重复独立抽样。判据未交给作答上下文。

逐项人工阅读两组原始输出后，六例未发现判据中的实质错误。基线已能保持关键状态、取消、资源和范围判断，本次不把它们计为新增改善。

| 请求 | 候选实际选择与结论 |
|---|---|
| L1 Icons | 直接读取 harmony-icons，保持同源生成、默认尺寸／颜色、无隐式主题及父控件无障碍；未虚构原生出口 |
| L2 Design | 直接读取 harmony-design／ui，区分基础数据、应用与系统字号、材质载体和宿主接管；未将确认作为业务成功 |
| L3 Camera | 直接读取 harmony-camera，对照 RN；非法／已取消新调用不接替，clear 先确认，选用移交，旧落盘单独收尾；补齐原计划未执行的拍照选用书面样本 |
| L4 Scan | 直接读取 harmony-hms-scan，保持真实读取结束后交还借用、旧轮隔离、单次交付和外观变化不重启设备 |
| L5 Umeng | 直接读取 harmony-umeng／integration，明确友盟与高德、真实回执、分享发出后的关闭边界和 SDK 缺口 |
| L6 Chat／共享／RN | 原生 Chat 读取 harmony-chat；共享 TS 检查全局及目标运行；RN 局部任务仍选 unif-design 与 RN 专题，未扩大鸿蒙范围 |

基线主要通过通则加 RN 专项契约补足细节；候选能从六库原生专题直接取得要求，仍按需对照 RN 行为。两组都诚实保留原生源码、SDK、设备等缺口。未单独运行“只更新规范”的第三组，因此不把差异归因于技能入口本身，也不宣称准确率或成本改善。

原始输入、输出、人工判定及日志保留于本地 `evals/code-development/runs/2026-10-27-harmony-library-foundation/`，不进入技能默认上下文。书面样本不证明宿主自动触发、编程准确率或设备功能。

## 独立审查

一次独立只读审查覆盖本轮规范、六库边界、生成及子目录路径、技能路由与证据陈述，结果为 Critical／Important／Minor 均无，可作为本地候选采用。原始报告保留在上述 runs 的 `review.md`。

审查未重复整套测试及书面评测，亦未评价产品构建、设备及真实业务验收。上述未评价项符合当前仅规范／技能的范围，继续保持未执行；它们不构成已完成鸿蒙产品能力的证据。

## 原线程采用建议

本任务未改 `ai-app-portal-harmony` 的任何文件。原线程如更新 `docs/development-baseline.md`，将验证入口切换到本报告和同名 JSON，采用该 JSON 的 SHA-256；两仓基线分支与 HEAD 不变，候选内容以新增清单为准。将“七个 harmony 专题”更新为“七个通则加六库专题，共十三个”；保留安装插件仍为 0.3.19、未发布及鸿蒙开发暂缓的说明。

项目原计划中“Camera 拍照选用书面专项尚未运行”可依据本报告 L3 的最终结果更新为书面样本已覆盖；必须继续保留原生拍摄实现、构建和设备验收未执行。无需为了采用规范创建 HAR、应用或原生示例。

## 完成层级与边界

源码检查、Python 自动化和分发／来源检查均属于规范与技能范围。此次没有产品构建、HAR／HAP 编译、模拟器／真机、厂商实际调用或业务验收；没有提交、推送、合并、发版或升级安装。候选可通过明确指定本地路径采用，宿主安装发现与长上下文遵守未验证。
