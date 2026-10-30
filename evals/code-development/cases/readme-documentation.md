# 库 README 与接入资料

当前迁移采用：通用组织、RN 实现、库工程与文档使用 uni-skills 的四个对应技能，code-development 核对企业采用及契约；历史基线输出保持原文，不回写为新版本结果。

本题为合成的成熟 RN 库，包名、SDK 和版本仅在题设内成立。提供技能发现目录、项目 AGENTS.md、下列工程片段，以及组织标准仓的指定修订；不提供 rubric 或参考答案。只处理文档，不执行安装、设备或远端操作。

修改前后冻结相同请求与工程片段；组织规范也有变化时，分别记录基线、仅更新规范、规范与技能一起更新的结果。原始输入、读取记录、输出与摘要留在本地 runs，不覆盖历史记录。

## 用户请求

整理这个库的 README，让接入者能快速判断它做什么、如何开始使用。保留已有能力和必要接入信息；本次只维护文档，不调整功能、依赖或发布配置。

## 工程事实

- 库已接入组织标准，有有效开发资料和正式文档站，不需要重新初始化。
- `selectMedia({ kind: 'image' })` 是现有公开 API，返回 `selected` 或 `cancelled`。iOS／Android 支持选择，Web 返回 `unsupported`；调用方负责选中临时文件的后续保存或释放。
- `docs/native-setup.md` 说明原生模块安装、权限、应用重建和宿主补丁。补丁由宿主维护，当前采用 `@example/native-media@4.3.2`；更新该依赖时需重新核对补丁与宿主行为。库不自动修改 SDK。
- `docs/DEVELOPMENT.md` 记录开发命令与验证基线：React 19.1.0、React Native 0.80.0、Native Media 4.3.2。已有原生构建记录，真实设备行为另行验收。
- `docs/api.md`、`example/README.md`、`LICENSE` 与文档站入口均存在。

`package.json` 相关片段：

```json
{
  "name": "@unif/react-native-media-kit",
  "peerDependencies": {
    "react": ">=19.1.0",
    "react-native": ">=0.80.0",
    "@example/native-media": "^4.3.0"
  },
  "devDependencies": {
    "@example/native-media": "4.3.2"
  }
}
```

## 当前 README

````markdown
# @unif/react-native-media-kit

提供媒体选择能力。支持 iOS、Android；Web 返回 unsupported。

[文档](https://unif-design.github.io/react-native-media-kit/) · [npm](https://www.npmjs.com/package/@unif/react-native-media-kit) · [API](docs/api.md) · [示例](example/README.md) · [许可](LICENSE)

## 接入

依赖 React 19.1.0、React Native 0.80.0、Native Media 4.3.2。所有消费者必须精确使用这一版本组合。宿主需安装原生模块、配置权限、应用对应 SDK 补丁、重新安装 Pods 并重建应用；完整步骤见 docs/native-setup.md。

```sh
npm install @unif/react-native-media-kit
```

```ts
import { selectMedia } from '@unif/react-native-media-kit';
const result = await selectMedia({ kind: 'image' });
```

结果可能是 selected 或 cancelled。选中临时文件的保存或释放由调用方负责。

## 开发验证

React 19.1.0、React Native 0.80.0、Native Media 4.3.2 是本次开发环境。运行类型检查、测试、Pods 安装、Android 和 iOS 构建后，再检查真实设备中的选择与取消。命令、构建记录与未验收项目见 docs/DEVELOPMENT.md。
````

请给出修订后的 README，以及需要同步的现有文档和核对项；说明采用的规则来源。不要把题设中的既有验证记录当作本次执行结果。
