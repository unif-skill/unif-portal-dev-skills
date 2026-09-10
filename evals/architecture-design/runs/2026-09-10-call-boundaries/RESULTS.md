# 调用边界的规范与技能入口对照

本次在固定任务和规范材料下运行三组、每组三个独立上下文。三组的调用边界及内部协调检查均通过：每组 17 项，共 51 项。已交付包也通过本题，所以没有观察到本次规范或入口调整带来的正确率增益；少量明确契约样本不能证明稳定性或生产效果。原始产出与类型表达待完善项均保留。

## 修改依据与版本

依据架构项目的 `docs/specs/2026-09-10-portal-development-skill.md` 及 `ARCHITECTURE.md` 第 3.1、6.1、7.4 节；源文件与 spec 的 SHA-256 见 [source-inputs.json](source-inputs.json)。spec 仍由架构项目维护，没有复制成技能仓手写规范。

- 同步脚本只改变 composition.md、contracts.md、verification.md 及 source.json，保留源文。开发规范的两份源文件及生成主题没有变化，未打包领域模块文档。
- architecture-design 改写已有职责、交接和阅读路由，要求核对调用决策、输入准备、结果复用与公共函数实际依赖。
- portal-development 改写已有架构协作条目，按调用与输入等实际设计变化选读功能组合和交接主题，继续使用已有依据足够时不扩读的入口规则。
- 两个 description 均未改变，没有加入按具体设备或查询命名的禁令。入口由 991 / 848 字符变为 1,029 / 878 字符，仍为 34 / 30 行。

| 组 | 规范材料 | 技能入口 | 用途 |
|---|---|---|---|
| A | 已交付包，架构源摘要 `4f191219…56f59` | 提交 `722ef37` | 原版本对照 |
| B | 更新后架构源，摘要 `b029877f…852da` | 与 A 相同 | 单独观察规范同步 |
| C | 与 B 完全相同 | 本次改写的两个入口 | 单独观察入口调整 |

A→B 只有三个生成主题和来源记录不同；B→C 只有两个 SKILL.md 不同。每组完整的模型文本材料冻结在 inputs，题目冻结在 cases，rubric 未提供给被测上下文。每次使用 `fork_turns: none`，不读取已安装技能、其他工程、作者讨论或其他答案；相同派发模板见 protocol.txt。模型继承主任务配置，未覆盖模型或推理参数；工具结果未给出可独立核实的模型 ID。运行环境为 Node.js v24.13.0，其他环境信息见 environment.json。

## 行为结果与人工核对

| 样本与判据 | 核对内容 | A | B | C |
|---|---|---|---|---|---|
| design：I1—I4 | 旧坐标不跳过明确刷新；定位完成后传新坐标；缺参零外部调用；输入只来自参数；单页查询；交互负责等待、翻页与后续确认 | 满足 | 满足 | 满足 |
| adapter：B1—B3 | 不从场景、草稿或缓存补参/跳过请求；一次指定页 list；无 detail 或自动翻页；成功码、缺值行、重复顺序与真实身份保持 | 满足 | 满足 | 满足 |
| internal：N1—N3 | 已确认 ensureDraft 内部查询及必要创建保留；设备选用和文件收尾保留；成功、取消、异常正确释放；等价文件整理不等全领域重设计 | 满足 | 满足 | 满足 |
| 可运行代码检查 | 直接导入各组 solution.mjs，使用替代 API、定位、设备和文件边界 | 17/17 | 17/17 | 17/17 |

人工逐份核对了必要类型、公共函数参数、实际依赖和设计结论。运行检查使用真实导出的 refreshNearby、queryNearby、readReasons、ensureDraft 和 capturePhoto，不复制实现或替换被测函数；调用记录、输入值、顺序和结果保存在 A/B/C-checks.json。合成方法名仅用于评测，不作为正式 API 或新产品需求。

C 组 readReasons 的读取日志包含功能组合、交接与验证等相关主题；内部文件整理样本也仅选择必要主题，没有加载全部架构资料。读取输出按冻结文件、行段与 SHA-256 可由 verify_reads.py 复核。该记录不验证真实宿主自动选取技能，也不测量模型总 Token。

检查器另做了四个故障注入探针：跳过重新定位、添加详情补查、移走复合操作的创建、遗漏临时文件清理，都触发了预期失败。具体单处替换和失败检查见 checker-probes.json；这些是检查器探针，不冒充被测模型的失败或独立样本。

## 保留的问题与限制

- 本次调用边界判据未发现不满足项。额外类型观察：C-design 的依赖接口成员仍内联 transport/location 的对象结构，没有像 A/B 一样完整整理成已命名依赖接口；该原文保留在 outputs/C-design/response.md。没有据此追加重复的类型禁令，也不凭单次差异归因于新入口。
- TypeScript 段落是未编译的契约方案，不属于运行检查通过范围。adapter 题目没有固定全部标识和展示值的原子类型，B 使用 unknown 保留这些未定值，A/C 使用字符串；本轮不据这些样本选择正式 API 值域或宣称完整类型验收。
- 输入等待、用户翻页和确认的交互归属经代码依赖检查与人工方案审查；没有运行真实 UI。资源清理检查只使用替身，不证明设备或真实文件系统行为。
- 各组每题仅一次。未测试其他模型、压缩上下文、真实宿主自动触发、业务消费者接线或真实 Portal 实现。全新上下文不等同于上下文压缩；未测 Token、费用或延迟收益。
- 被测上下文自行描述的其他本地测试仍作为原始输出保存；本报告统一计数只采用主任务复核的 17 项/组，不把自报数量累计成额外独立证据。

## 同步、分发与安装

37 项同步/仓库脚本测试通过；两种规范 `--check` 通过。两个完整技能分别复制到独立临时目录，在没有另一个技能及架构源目录的包内校验中，格式和所有相对引用均通过，见 portable-checks.json。此检查验证可移位读取，不验证所有缺失协作技能的运行场景。

本次只读检查了当前会话列出的 `0.0.1` 缓存目录：仅有 architecture-design，其入口摘要与当前仓库不同，没有 portal-development。路径与摘要见 installed-copy.json；不把该目录检查推广为所有缓存或宿主实际加载状态。没有发布、安装或重载操作，因此仓库改动不代表当前安装已生效。

原有 runs 的冻结文件摘要保持不变。规范、spec 及当前分发材料在评测结束时再次核对；本次没有修改 Portal 工程或架构源，没有提交、推送、发布、安装或发送跨任务通知。

## 本地复核

```sh
python3 evals/architecture-design/runs/2026-09-10-call-boundaries/verify_reads.py
node evals/architecture-design/runs/2026-09-10-call-boundaries/check-behavior.mjs evals/architecture-design/runs/2026-09-10-call-boundaries/outputs A
node evals/architecture-design/runs/2026-09-10-call-boundaries/check-behavior.mjs evals/architecture-design/runs/2026-09-10-call-boundaries/outputs B
node evals/architecture-design/runs/2026-09-10-call-boundaries/check-behavior.mjs evals/architecture-design/runs/2026-09-10-call-boundaries/outputs C
```

复跑只读取冻结材料并调用合成依赖，不访问真实服务或安装模型。完整分发包与记录摘要继续通过仓库的 validate_repository.py 校验；外部源的新鲜度通过同步脚本 --check 单独核对。
