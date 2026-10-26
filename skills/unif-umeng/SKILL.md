---
name: unif-umeng
description: 在接入、维护或排查 @unif/react-native-umeng 的隐私同意后初始化、统计、第三方分享、分享面板或平台回调时使用。
metadata:
  package: "@unif/react-native-umeng"
---

# Unif Umeng

先核对应用锁文件、实际安装包或本次维护修订的 package.json、exports 与公开类型。[官网索引](https://unif-design.github.io/react-native-umeng/llms.txt) 标明文档构建版本；版本不一致时从对应安装包或已核实发布修订取得接口，不能直接采用最新文档的新增能力。

## 按任务读取

本地源码的使用文档在 website/docs；没有库工作区时使用下面的公开资料。只读当前任务相关单页，全文是确需全局资料时的选项。

| 任务 | 使用资料 |
|---|---|
| 安装与快速接入 | [getting-started/installation](https://unif-design.github.io/react-native-umeng/md/getting-started/installation.md)、[getting-started/quick-start](https://unif-design.github.io/react-native-umeng/md/getting-started/quick-start.md) |
| 隐私同意与初始化 | [guides/privacy-pipl](https://unif-design.github.io/react-native-umeng/md/guides/privacy-pipl.md)、[api/common](https://unif-design.github.io/react-native-umeng/md/api/common.md) |
| 直接分享与结果 | [guides/sharing](https://unif-design.github.io/react-native-umeng/md/guides/sharing.md)、[api/share](https://unif-design.github.io/react-native-umeng/md/api/share.md) |
| 实例分享宿主与呈现 | [api/platform-sharesheethost](https://unif-design.github.io/react-native-umeng/md/api/platform-sharesheethost.md) |
| 统计与原生回调 | [guides/analytics](https://unif-design.github.io/react-native-umeng/md/guides/analytics.md)、[api/analytics](https://unif-design.github.io/react-native-umeng/md/api/analytics.md)、[native-setup/ios](https://unif-design.github.io/react-native-umeng/md/native-setup/ios.md)、[native-setup/android](https://unif-design.github.io/react-native-umeng/md/native-setup/android.md) |
| 测试与排障 | [testing](https://unif-design.github.io/react-native-umeng/md/testing.md)、[troubleshooting](https://unif-design.github.io/react-native-umeng/md/troubleshooting.md) |

## 使用边界

应用取得真实隐私同意后再调用 initializeUmeng；库不拥有用户同意记录。导入包、显示面板和接收系统回调不等于完成初始化。配置与凭据不写入模型输入、日志或分享结果。

直接分享查 share，目标选择查 useShareSheet。控制器与 host 属于同一实例，宿主放在实际展示窗口；图片准备和上传使用应用已有能力。SDK 有效成功回执、用户取消、失败和 busy 分别处理；面板关闭或应用被拉起不能证明分享成功。

## 实施与验证

本技能可单独使用，完整操作和维护依据见[任务指引](references/workflows.md)。应用消费采用公开接口和已有能力；源码维护从库内 docs/DEVELOPMENT.md 取得工程指定的规范。工程已配置共用阶段技能时按需使用，无需为本技能另行安装。复用同一任务已取得的有效依据。

验证实际输入、事件、结果与消费者，保留本库取消、错误和资源保护；检查命令从当前 package.json/CI 取得。只查询接口或版本时回答已核实事实，不自动修改代码、安装依赖或执行发布。
