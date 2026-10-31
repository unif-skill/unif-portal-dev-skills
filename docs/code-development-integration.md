# 工程技能入口

每个技能的完整目录可以独立使用。工程入口列明实际采用的规范位置和适用技能，按已安装描述选择当前任务；不把另一技能或某个插件缓存路径作为前置条件。

## 入口示例

```markdown
## 开发规范

- 采用本工程确认的业务契约、规范修订和实际配置；按已安装技能的描述选择当前任务入口。
- RN 开发、测试和审查按实际工作选择 rn-development、rn-testing、rn-review；原生鸿蒙选择 harmony-development、harmony-testing、harmony-review；Python 后端选择 backend-development、backend-testing、backend-review。
- 跨平台设计和交付分别使用 architecture-design、code-delivery；每个完整目录自身包含必需规则，测试和审查不依赖开发技能。
- 已安装的库能力技能可辅助定位公开 API，未安装时直接使用本库对应版本文档和类型。
- 同一上下文有效依据直接复用；实际命令、门禁、发布方式及操作授权从本工程和当前任务取得。
```

只保留工程实际采用的条目，并填写可访问的规范位置；示例不是安装清单。原 code-development、code-testing、code-review 引用按工程平台迁移到上述入口，单独安装时移除已替换的旧目录。RN 的 iOS／Android 差异仍在 RN 技能内按需处理。

RN 技能只补充 Unif 企业约定，不复制通用 react-native-development；目标工程说明通用规则的有效来源，不要求安装 uni-skills 或某个固定插件。

## 资料与运行边界

共同规范由同一架构源生成到使用它的技能目录。RN、鸿蒙、后端各阶段技能只携带所属平台的主题；共同契约在各自 references/common/。code-delivery 按交付目标选读本目录的验收资料。根同步器、测试和 evals 只用于维护，不进入独立技能运行依赖。

包内快照提供通用的 Unif 契约和验收规则；目标工程仍提供实际业务契约、采用版本、代码、命令与验证证据。状态表按本次范围读取，不随技能打包成固定状态。平台正文不把 RN 接口套到 ArkUI，库不套 Portal 业务目录。

Unif RN 库组织接入使用 code-delivery 随附的非敏感组织资产，复制为工程 `.github/organization.json` 后落实到实际配置。已有 `.github/delivery.json` 和 `.github/scripts/check-delivery.cjs` 时按本库定义检查；CI 只读取工程文件，无需安装技能。该组织资产不用于鸿蒙 HAR 或后端，私钥与令牌保留在平台。

源码修改、同源生成、格式与脚本校验、模型实际消费、安装及真实工程验收分别验证。技能维护不自动授权提交、推送、发布、安装或设备任务。
