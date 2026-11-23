---
name: unif-oss
description: 处理 @unif/react-native-oss 的临时凭证、上传回执和源文件释放，涵盖单文件上传、远程转存与顺序批量上传。服务端 OSS SDK 和桶权限另按服务端配置处理。
metadata:
  package: "@unif/react-native-oss"
---

# Unif OSS

先从应用锁定版本的根导出选择临时凭证、单文件上传、远程转存或顺序批量接口。对应文档在库的 `docs`。官网构建版本不同时，按已采用的包或修订核对字段。[API 与版本索引](https://unif-design.github.io/react-native-oss/llms.txt)

## 把凭证接到已有上传入口

宿主提供当前账号、HTTP 换发和 `ossKey` 白名单。长期密钥留在服务端，客户端使用临时凭证，也可用 `createOssCredentialAccess` 在当前身份内管理它。请求限定在原白名单内。单次取消只结束所属等待，身份结束时调用 `dispose`，忽略迟到的换发响应。诊断记录中省略凭证和原始服务响应。[凭证与对象归属](https://unif-design.github.io/react-native-oss/md/contract.md)

## 上传取消或回执未知时，文件能否释放

| 观察到的事件 | 可以判断什么 |
|---|---|
| `onRequestStarted` | 已取得即将发送的对象身份，可保存作后续核对。 |
| 上传回执 | 按该次实际结果处理成功、拒绝、未确认或取消。未确认时保留原对象并避免自动重传，业务保存另查其回执。 |
| `onSourceReleased` | 已确认原生不再读取本地源文件，调用方此时才归还自己的文件持有。 |

远程转存只清理本次私有临时文件。批量按输入顺序执行，保留重复项、每项回执、已成功项和未开始项。[单文件、转存与批量 API](https://unif-design.github.io/react-native-oss/md/api.md)

维护时从上传消费者追到实际 SDK 补丁及原生终态回调。核对晚到的回执、文件只释放一次，以及清理失败后仍能取得原对象回执。[原生接线](https://unif-design.github.io/react-native-oss/md/native-setup.md) · [维护与消费者验证](references/workflows.md)
