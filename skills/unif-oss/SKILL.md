---
name: unif-oss
description: 在查询、接入、维护或排查 @unif/react-native-oss 的临时凭证、单文件上传、远程转存、顺序批量、上传回执及源文件释放时使用。不用于服务端 OSS SDK 或桶权限配置。
metadata:
  package: "@unif/react-native-oss"
---

# Unif OSS

先核对应用采用版本、锁文件、exports 和公开类型；[官网索引](https://unif-design.github.io/react-native-oss/llms.txt) 的版本不同于安装包时，使用对应包或已核实修订的资料。凭证与原始服务响应不进入技能材料。

## 按任务读取

本地资料位于 docs，website/docs 链接到同一来源；只读当前操作的章节。

| 任务 | 资料 |
|---|---|
| 凭证校验、访问实例与取消 | [API](https://unif-design.github.io/react-native-oss/md/api.md) 的临时凭证部分 |
| 单文件、远程转存与批量 | [API](https://unif-design.github.io/react-native-oss/md/api.md) 对应部分 |
| 身份、对象回执与文件归属 | [行为与所有权](https://unif-design.github.io/react-native-oss/md/contract.md) |
| SDK 终态回调、补丁与消费者验证 | [原生接线](https://unif-design.github.io/react-native-oss/md/native-setup.md) |
| 应用接入与源码维护 | [任务指引](references/workflows.md) |

## 使用边界

宿主持有账号、HTTP 换发适配与 ossKey 白名单，createOssCredentialAccess 管理该实例内的临时凭证。身份结束时 dispose；单次取消和实例失效结束本地等待，迟到响应不能写入新缓存。不改用长期密钥，不扩大 key 范围。

onRequestStarted 只交付即将发送的对象身份；成功、拒绝、未确认与取消依据实际回执处理，未确认对象不自动重传。Promise 或清理完成不证明上传、远端状态或业务保存成功。

本地源文件归调用方，等待 onSourceReleased 确认不再读取后再释放。远程转存只管理本次私有临时文件。批量保留输入顺序、逐项结果和未开始项，不默认去重、回滚或并行化。

## 实施与验证

本技能可单独使用；维护时核对 docs/DEVELOPMENT.md、公开源码与实际消费者。检查命令从当前工程取得。库 Mock、实际修补 SDK、原生构建、设备取消和真实 OSS 回执分别验证；查询接口不授权请求凭证、上传或发布。
