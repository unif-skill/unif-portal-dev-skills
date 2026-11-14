# Unif RN 库 GitHub 采用

本专题仅适用于 Unif RN 库。读取本技能的[组织资产](../assets/organization.json)，核对目标仓库与当前授权后，将其复制为目标工程 `.github/organization.json`。已有文件先比较来源、内容和本次已批准差异；不覆盖未核实的工程选择。执行采用工具时传入工程内路径，不读取另一个技能的安装目录。

资产保存非敏感组织值：GitHub owner、npm 名称规则、Pages URL 规则、发布 App ID、仓库设置、安全策略及停用文件清单。App ID 是公开身份，私钥和令牌仍在平台凭据配置中；不复制到资产、源码、日志或命令示例。

## 落实到工程

- 以实际 package.json、文档站和 workflow 确定需要的接线；命令及共享文件采用记录保留在目标工程。已有 `.github/delivery.json` 与 `.github/scripts/check-delivery.cjs` 时使用其实际检查方式。
- repositorySettings 控制仓库合并与安全扫描设置。远端操作按授权用当前已登录的 gh CLI 执行并回读，不把本地 JSON 当成远端已生效。
- 有文档部署 workflow 时采用 Pages Actions 来源，网址按 pagesURL 中的 `{repo}` 替换为实际仓库名；同步 About 网站入口。没有文档部署的工程不因资产存在自动建站。
- security 的三项分别核对 CodeQL 默认配置、Dependabot 安全更新和私密漏洞报告；不从其中一项推断其他项已完成。
- 对照组织资产的 `obsoleteFiles` 逐项核实并清理已停用配置。远端 Dependabot 安全更新开关按 `security` 单独核对。

成熟库局部修改复用有效采用记录，不重新初始化或反复设置远端。规则和资产更新、工程接入、离线漂移检查及远端生效分别留证；权限不足时只限制依赖该权限的步骤，不自行申请更大权限或改用个人凭据绕过。
