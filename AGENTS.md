# 技能仓维护入口

使用中文交流。本仓维护 22 个可独立分发的完整技能目录；按 RN、鸿蒙、后端的平台与阶段职责维护当前入口，不要求消费者安装其他技能。

- 先核对当前 spec、计划、实际目录和未提交修改；技能维护使用 skill-creator、writing-skills，文档维护使用 uni-documentation。通用流程按本次任务和已安装技能描述选择。
- 本次独立化及 1.0.0 范围见[契约](docs/specs/2026-10-30-independent-skills-v1.md)与[计划](docs/superpowers/plans/2026-10-30-independent-skills-v1.md)。已有业务契约、历史验收与用户授权继续有效，不因重排资料扩大任务。
- 生成主题先改 unif-platform-architecture 的对应规范，再运行 scripts/sync_architecture.py；不手改生成正文或 source.json。按阶段选取的资料保留同源摘要、选取范围与覆盖校验。
- RN 专题只承接 Unif 的目录与环境采用、库选型、业务及视觉契约和实际消费者验收。React／Hooks、通用文件组织、平台安装调试、测试选择及库工程流程由通用标准维护，不在本仓另写流程或建立跨技能文件依赖。
- 鸿蒙专题只承接 Unif 项目采用、模块职责、业务契约和具体消费者验收。ArkTS／ArkUI、SDK 支持表、状态机制与 HAR 工程流程由通用标准维护，不在本仓另写或生成平台通用正文，也不建立跨技能文件依赖。
- 根 scripts、tests、evals 和 docs 仅用于维护。独立技能运行必需资料、资产及工具放在自身目录，不引用兄弟目录、根维护脚本或个人缓存路径。具体业务 API 和当前工程配置仍从目标工程取得。
- unif-code-delivery/assets/organization.json 仅维护 Unif RN 库非敏感组织值；接入时写入目标工程，不将私钥或令牌入库。修改资产同时核对其专题、真实消费者和必要校验。
- 使用现有 Python 依赖执行脚本回归、分发包校验及受影响同步 --check，核对实际读取范围；格式、行为、安装及真实工程验收分别报告。
- 常规发布允许 minor／patch：自当前版本标签以来的待发布提交含 `feat` 类型时升 minor 并将 patch 归零，其余升 patch；显式指定的同 major 新版本保留。自动发布保持已发布 major，跨 major 变化须单独明确授权。普通维护不授权提交、推送、发布或安装，也不改已安装缓存。
