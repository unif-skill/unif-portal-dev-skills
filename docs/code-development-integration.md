# 工程开发入口

目标工程的 AGENTS.md 指向实际采用的规范与契约。保留影响本工程执行的版本、平台边界和验证命令。开发者安装插件见[安装与使用](../README.md#安装与使用)。

例如，Portal 的工程入口链接到采用的[平台架构](https://github.com/unif-design/unif-platform-architecture/blob/main/ARCHITECTURE.md)和[开发状态](https://github.com/unif-design/unif-platform-architecture/blob/main/STATUS.md)，模块文档给出真实接线与验证入口。原生鸿蒙库核对采用版本的 HAR 实际导出。

Unif RN 库的组织接入使用 unif-code-delivery 随附的非敏感组织资产，复制到工程的 `.github/organization.json`。已有 `.github/delivery.json` 和 `.github/scripts/check-delivery.cjs` 时按本库定义检查。该组织资产仅适用于 RN 库，私钥与令牌保留在平台。
