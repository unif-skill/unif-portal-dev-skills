---
name: unif-logger
description: 接入或排查 @unif/react-native-logger 和原生鸿蒙 @unif/harmony-logger 的日志运行时、身份关联、脱敏、私有存储与诊断快照。通用日志规范、普通 Python 日志和其他日志框架另查各自资料。
metadata:
  package: "@unif/react-native-logger"
  harmony_package: "@unif/harmony-logger"
---

# Unif Logger

RN 使用 `/files` 文件入口，Web 同一入口采用有界内存。查询公开接口时先看应用锁定版本，和官网构建版本不同时，查对应包或修订。[RN 与 Web 接入](references/rn.md) · [官网索引](https://unif-design.github.io/react-native-logger/llms.txt)

接入原生鸿蒙 `@unif/harmony-logger` 时，从宿主依赖定位同仓 HAR 或已安装的包，核对其公开入口和宿主实际接线。采用版本提供 `/Files` 时，通过该入口使用文件能力。[鸿蒙公开入口与接入](references/harmony.md)

## 让业务日志使用已有运行时

宿主统一安装运行时，管理策略、身份和私有存储。业务模块复用公开 logger，在操作开始时固定关联上下文，始终绑定原身份、原运行时和进程。使用公开字段和脱敏方式，凭据在进入日志接口前剔除，业务正文按宿主策略处理。[日志字段与格式](https://unif-design.github.io/react-native-logger/md/FORMAT.md)

主字段、附日志和快照各用所属接口。遇到分类大内容需求，先核对采用版本能否采集、索引、读取、限额和释放。具体缺口交给宿主或库维护者，沿用原有文件管理。

## 日志未落盘或快照不能读

- **写入**　从生产者追到存储。两端的 0.3.0 接口通过 `await logger.captureError(...)` 取得规范化文本或 `null`。`flush` 或 `setOwner` 结算后检查文件健康状态。记录故障时保留原业务结果和重试行为，避免递归写入同一失败通道。
- **清理或切换身份**　`clear` 保留活跃快照，要看实际清理结果。切换身份或 `dispose` 会使未交付的快照句柄失效。
- **交给分享或上传方**　`takeSnapshotFile` 成功后，文件归接收方。即使切换账号，也要等对方实际读完再调用 `file.release`。[RN 快照与文件交接](https://unif-design.github.io/react-native-logger/md/api/files.md)

维护时从实际采用的实现和平台适配入手，用日志生产者和文件接收方核对脱敏、关联、旧身份写入、存储失败及清理后的释放。各端按本端宿主验证。[RN 源码维护](https://unif-design.github.io/react-native-logger/md/DEVELOPMENT.md) · [鸿蒙模块与维护](references/harmony.md)
