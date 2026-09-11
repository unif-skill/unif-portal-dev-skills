# 缓存维护题设

这是合成工程；以下资料构成本题全部代码和需求，不读取真实业务仓库，不修改代码或设备。

请为当前 App 的“统计临时缓存、用户清理缓存”功能给出实现选择和需要的验证，控制在 450 字内。调用方只需要 `measure(): Promise<number>` 和 `clear(): Promise<void>`，清理保留缓存根目录，不影响登录凭据和持久文件，失败如实返回。不需要下载、同步或业务上传。工程已有文件依赖 A、B，均已链接到两个原生平台；不要新增产品操作。

已安装库 A 的公开能力：`cacheDirectory`、`readDirectory(path)`、`stat(path)`、`remove(path)`。单项大小可读，目录需汇总。Android remove 调用递归删除，然后 resolve；其底层代码为 `children.forEach(remove); file.delete();`，不检查删除布尔结果。

已安装库 B 的公开能力：`dirs.cache`、`list(path)`、`info(path)`、`unlink(path)`。list 返回名称，info 返回文件/目录类型与文件大小；unlink 负责目录递归，Android 删除失败抛错并使 Promise reject，iOS 同样回报删除失败。两库都没有公开“不跟随符号链接”的接口。没有发现实际缓存写入方创建符号链接，也没有指定此类文件处理需求。

团队已有一个建议：由于 A 的删除失败不可靠，新增 Android 原生模块并实现独立的文件访问接口。现在目录和接口草稿还未写。请决定是否采用，说明保留哪些应用代码、复用什么、哪些结论仍需验证。不要把源码片段或测试替身当真机结果。
