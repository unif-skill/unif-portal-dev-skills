# 原生鸿蒙 Umeng

先读 [harmony-umeng README](https://github.com/unif-design/harmony-umeng/blob/main/README.md)、[包清单](https://github.com/unif-design/harmony-umeng/blob/main/library/oh-package.json5)及 main 入口，再读取[原生目标契约](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-umeng.md)。本地按相同相对路径定位，采用版本、目标规范与实际公开 API 分别核对。

若当前只有空 HAR 或 `export {};`，不能直接接入友盟初始化、统计或分享。只说明契约和缺口，不将 RN initializeUmeng、share、useShareSheet 或 iOS／Android 回调配置当作鸿蒙实现。技能查询不授权安装 SDK、配置凭据、执行分享或恢复原生开发。

## 目标职责

应用持有真实隐私同意、账号、截图、上传和业务结果；库承接友盟初始化、就绪／渠道查询、统计与分享能力。采用真实鸿蒙友盟 SDK、版本与渠道要求，不能以系统分享面板替代已确认的供应商能力，也不引入地图职责。

隐私同意前不隐式初始化或缓存业务事件。进程 SDK 就绪、单次分享和面板呈现分开；宿主、回调和临时资源按实际 UIContext／Ability 生命周期管理，不能每页再维护一套分享流程。

分享成功依赖本次渠道的有效 SDK 回执。关闭面板、拉起外部应用或 void 返回不能当作成功；厂商调用发出后取消呈现不等于撤销分享。未知回执保留不确定性，旧回调不操作新面板。临时文件等真实读取结束后释放，凭据与分享内容不写日志。

## 实施与验证

获授权实现时，从所属仓库入口、有效目标契约和厂商资料核对配置、支持渠道、回调、并发与资源，保持独立统计／查询不依赖分享 UI。

源码／自动化、HAR 与宿主构建、真实渠道 App 的成功／取消／失败、统计接收及业务同意链分别验收。空包、系统面板演示或 Mock 不能替代友盟 SDK 与真实服务证据；缺少凭据或设备时明确相应未验证范围。
