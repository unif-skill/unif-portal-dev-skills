# 工程技能入口

在目标工程的 AGENTS.md 中列出实际采用的规范位置和技能名。

## 入口示例

```markdown
## 开发规范

- 采用本工程确认的业务契约、规范修订和实际配置；按已安装技能的描述选择当前任务入口。
- RN 开发、测试和审查按实际工作选择 unif-rn-dev、unif-rn-test、unif-rn-review；原生鸿蒙选择 unif-harmony-dev、unif-harmony-test、unif-harmony-review；Python 后端选择 unif-python-dev、unif-python-test、unif-python-review。
- 跨平台设计和交付分别使用 unif-architecture-design、unif-code-delivery。工程共用的状态归属、交接契约和验证依据从 unif-platform-rules 的对应主题读取。
- 库能力技能随同名插件按库安装，已安装的库技能可辅助定位公开 API，未安装时直接使用本库对应版本文档和类型。
- 同一上下文有效依据直接复用；实际命令、门禁、发布方式及操作授权从本工程和当前任务取得。
```

只保留工程实际采用的条目，并填写可访问的规范位置；示例不是安装清单。RN 的 iOS／Android 差异仍在 RN 技能内按需处理。

## 资料与运行边界

工程指定实际业务契约、采用版本、命令与状态表。平台规范的来源、分发方式和运行边界见[规范来源](../README.md#规范来源)和[使用与分发](../README.md#使用与分发)。原生鸿蒙接口以所用 HAR 的真实出口为准。

Unif RN 库组织接入使用 unif-code-delivery 随附的非敏感组织资产，复制为工程 `.github/organization.json` 后落实到实际配置。已有 `.github/delivery.json` 和 `.github/scripts/check-delivery.cjs` 时按本库定义检查；CI 只读取工程文件，无需安装技能。该组织资产不用于鸿蒙 HAR 或后端，私钥与令牌保留在平台。
