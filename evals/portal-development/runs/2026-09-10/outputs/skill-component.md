本批只整理 ChoicePanel 单元，在已有交互契约下保持页面与聊天复用；客户查询、选择流程及草稿保存继续由订单入口负责。按指定 `portal-development` 技能及其开发规则第 2—5 节、工程组织第 1—2、4、6 节，将已经存在的 props、中文固定文案与样式分别放回组件自己的角色文件。这里的配套拆分属于 ChoicePanel 本批修改，不扩展到其他组件或业务功能。

文件树（以题设的 components 为起点）：

```text
components/
├── ChoicePanel/
│   ├── ChoicePanel.tsx   # 修改：展示及回调接线
│   ├── types.ts          # 本组件实际需要的展示类型和 props
│   ├── constants.ts      # 已有中文空态文案
│   ├── styles.ts         # 依当前主题生成样式
│   └── index.ts          # 小型公共入口；若已有则保留原有必要出口
└── CellList/
    └── index.ts          # 已有具名导出，复用；不修改本单元
```

关键文件内容如下。`react-native` 和设计系统采用公开导出；设计系统入口依据包内工程组织规则。题设未给出真实工程依赖、解析配置和文件内容，因此这些导入仍需在目标工程核对，不构成已验证的 SDK 结论。

`components/ChoicePanel/types.ts`：

```ts
export interface ChoiceItem {
  id: string;
  title: string;
}

export interface ChoicePanelProps {
  items: readonly ChoiceItem[];
  onSelect: (id: string) => void;
}
```

`components/ChoicePanel/constants.ts`：

```ts
export const EMPTY_MESSAGE = '暂无选项';
```

`components/ChoicePanel/styles.ts`：

```ts
import { StyleSheet } from 'react-native';
import type { ColorValue } from 'react-native';

export function createStyles(backgroundColor: ColorValue) {
  return StyleSheet.create({
    root: { backgroundColor },
  });
}
```

`components/ChoicePanel/ChoicePanel.tsx`：

```tsx
import { Text, View } from 'react-native';
import { useColors } from '@unif/react-native-design';
import { CellList } from '../CellList';
import { EMPTY_MESSAGE } from './constants';
import { createStyles } from './styles';
import type { ChoicePanelProps } from './types';

export function ChoicePanel(props: ChoicePanelProps) {
  const colors = useColors();
  const visibleItems = props.items;
  const styles = createStyles(colors.background);

  return (
    <View style={styles.root}>
      {visibleItems.length === 0 ? (
        <Text>{EMPTY_MESSAGE}</Text>
      ) : (
        <CellList items={visibleItems} onSelect={props.onSelect} />
      )}
    </View>
  );
}
```

`components/ChoicePanel/index.ts`：

```ts
export { ChoicePanel } from './ChoicePanel';
```

消费方可通过对应组件目录的公共入口具名导入 `ChoicePanel`。保留主实现的具名导出，现有消费者的具体导入是否需要调整，要依据目标工程中的静态引用检查确定，不假设它们目前使用某个别名。题设没有展示消费者需要显式导入 props 或条目类型，因此公共 index 只导出组件；`types.ts` 中的 export 用于单元内协作。若真实消费者确需这些类型，再从此小型入口选择性导出，不能据此导出所有内部类型。

`colors`、`visibleItems`、`styles` 是本次渲染得到的值，仍留在组件调用作用域；它们使用 `const` 不代表固定常量。样式工厂接收当次主题的背景 token，主题变化后随渲染重新生成样式，不把主题值捕获成模块级固定值。`visibleItems` 保留原数组及条目顺序，不新增过滤或选择规则。没有消费者的 `selected` ref 以及对应的 `useRef` 导入直接删除，不迁往状态文件。`length === 0` 直接表达空数组条件即可。

不采用题设提出的其他扩展：

- 不新增 `BaseButton`。本次没有按钮需求，也没有补充设计系统的组合职责。
- props 和条目展示结构放在 ChoicePanel 自己的 `types.ts`，不进入全局 `src/types/customer.ts`，不引入客户领域模型。
- ChoicePanel 只接收条目与回调，不读取订单 store、不查询客户、不保存草稿，也不新增确认或提交操作。
- `constants.ts`、`styles.ts` 有上述实际内容才创建；本次不存在边界校验需求，不建 `schema.ts`，不建 `variables.ts`，也不建可变状态文件或无意义的平台版本。
- 不建立导出全部组件及内部类型的 `components/index.ts`。ChoicePanel 使用 CellList 已有公共入口，不穿透它的实现文件。

CellList 没有自己的命名固定值时，无需增加 `constants.ts`，更无需统一补齐空 `styles.ts`、`schema.ts`、`variables.ts`。如果其自身有显式类型、样式，应按自身实际内容及修改范围维护；本题没有要求修改 CellList，也没有提供其内部实现，不凭目录模板重排它。

验证范围：

1. 在目标工程使用既有 TypeScript、ESLint 及已有导入检查，核对新相对路径、设计系统公开导出、`colors.background` 与 `ColorValue` 的类型兼容、CellList 的条目及回调兼容、没有遗留 `useRef` 引用；检查 ChoicePanel 及其类型消费者的导入。按实际 JSX 编译配置判断是否需要显式 React 导入。
2. 优先运行通用组件已有的 ChoicePanel 渲染测试，以其实际需要的轻量主题宿主验证空数组仍显示“暂无选项”、非空时条目与顺序保持、选择动作把对应 id 交给传入回调、主题背景在主题切换后更新。已有断言不足时只补充这些受影响行为，不复制 CellList 或设计系统内部测试。
3. 对订单选择弹层和聊天选择面板运行实际受影响的组合测试，核对公共入口可加载、条目正常展示及选择回调接线保持。订单端原有查询及保存责任不变，组件不产生业务请求。
4. 单独检查 Web 预览宿主的导入、编译和实际渲染，包括主题及选择交互；原生渲染测试通过不能代替 Web 预览证据。该变更没有新增设备能力，不默认要求全领域测试或原生 SDK 集成测试；目标工程既定合并、发布门禁仍按其配置执行。

本答复仅完成题设和指定技能材料的书面核对，未访问目标工程、SDK 或业务系统，未安装依赖、运行类型检查、测试、Web 构建或设备验证。以上检查是待在目标工程执行的定向范围；没有把规范要求表述为现有 CI 已强制落实，也不宣称实现已经编译或测试通过。
