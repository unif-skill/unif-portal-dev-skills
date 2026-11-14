---
name: unif-logger
description: 在查询、接入、维护或排查 @unif/react-native-logger、@unif/harmony-logger 的公开 API、运行时、脱敏、关联、私有存储和快照交接时使用。通用日志规范、Python 日志及其他日志框架不单独触发。
metadata:
  package: "@unif/react-native-logger"
  harmony_package: "@unif/harmony-logger"
---

# Unif Logger

按宿主使用的平台和锁定版本核对日志包的公开出口，采用版本与官网不同则读对应修订。

## 按平台查阅

| 目标 | 资料 |
|---|---|
| RN／Web 根入口、`/files` 与实际消费者 | [RN 指引](references/rn.md)、[RN 官网索引](https://unif-design.github.io/react-native-logger/llms.txt) |
| 原生鸿蒙根入口、`/Files`、HAR 与共享核心 | [鸿蒙指引](references/harmony.md)、[HAR 包文档](https://github.com/unif-design/harmony-logger/blob/main/library/README.md) |

## 接入与生命周期

宿主持有一套运行时及其策略、存储和身份，生产者复用公开 logger；不在各业务模块另装运行时、建日志目录或切换账号。创建操作时固定上下文，核对异步与身份切换后的有效性，不跨身份、运行期或进程复用上下文对象。字段和安全原因使用所采用版本的公开能力，不自行解析任意异常文字或复制 formatter。

主日志字段、附日志和快照分别按真实 API 交接。需求涉及分类大内容时，先核对采用版本是否提供采集、索引、读取、容量和释放能力；缺少能力明确报告给宿主或库维护范围，不把快照接口冒充单次大内容存储，也不在业务层补写第二套文件管理。凭据不交给任一日志接口，业务正文按宿主治理策略处理。

`captureError` 返回文本不证明落盘，`flush` 或 `setOwner` 完成仍需核对健康状态。日志失败不能改变业务成功、异常或重试；对接口的返回、抛错和健康信息按采用版本处理，不递归写失败通道。

未交付快照、已交付文件和源日志分别管理。`clear` 保留活跃快照；身份切换和 `dispose` 使未交付快照失效，不提前删除已交付文件。`takeSnapshotFile` 转移所有权后，等待接收方实际读取结束再调用 `file.release`，分享面板打开或上传取消不证明已经读完。

## 验证与交付

沿生产者、运行时、私有存储和实际读取消费者核对关联、脱敏、健康状态与资源释放，覆盖旧身份、迟到写入及存储失败。查询版本或接口不执行真实日志导出、上传或安装。源码／替身、实际包或 HAR 消费、平台构建、设备文件行为和发布安装分别报告；共享测试不证明另一平台已发布或真实磁盘可用。
