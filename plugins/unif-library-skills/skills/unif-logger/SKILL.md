---
name: unif-logger
description: 在查询、接入、维护或排查 @unif/react-native-logger 或 @unif/harmony-logger 的结构化日志、脱敏、身份隔离、文件存储、诊断快照及共享核心时使用。不用于其他日志框架或普通业务文件管理。
metadata:
  package: "@unif/react-native-logger"
  harmony_package: "@unif/harmony-logger"
---

# Unif Logger

先确定 RN／Web 或原生鸿蒙，以及应用消费、库维护或共享核心任务。核对实际包版本、公开出口与安装产物；RN 文档版本和鸿蒙采用修订分别确认，不能将同名能力视为两端已同步。

## 按平台读取

| 目标 | 资料 |
|---|---|
| RN／Web 根入口、`/files` 与实际消费者 | [RN 指引](references/rn.md)，公开版本入口为 [RN 官网索引](https://unif-design.github.io/react-native-logger/llms.txt) |
| 原生鸿蒙根入口、`/Files`、HAR 与共享核心 | [鸿蒙指引](references/harmony.md)，公开接口见 [HAR 包文档](https://github.com/unif-design/harmony-logger/blob/main/library/README.md) |

只读取当前平台与任务需要的资料。维护共享核心时再对照双方采用记录；单平台消费不要求安装另一平台或其他技能。

## 共同边界

应用安装并持有一套日志运行时，统一策略、存储和身份；库生产者复用 createLogger，不自行初始化或切换账号。环境与安全身份摘要来自宿主，操作上下文不跨身份、运行期或进程复用。

先使用白名单字段与受控诊断，避免把凭据、请求正文或完整业务对象交给日志。日志记录不决定业务成功；captureError 返回文本不证明落盘，flush 或 setOwner 完成仍需结合健康状态判断存储失败。

未交付快照、已交付文件和源日志分别处理。clear 保留活跃快照；身份切换和 dispose 使未交付快照失效，但不提前删除已交付文件。takeSnapshotFile 转移所有权后，等接收方真正读完再调用 file.release，不能按分享面板打开或上传取消提前释放。

## 实施与验证

复用当前公开入口与已有宿主；只查询版本或契约时不安装、导出或上传日志。维护读取所属库开发说明、实际生成来源和消费者，保留身份、脱敏、资源与错误处理。

源码／Mock、RN 实际包或 HAR 消费、平台构建、设备文件行为及发布后安装分别报告。共享测试通过不证明两端已发布或实际磁盘可用。
