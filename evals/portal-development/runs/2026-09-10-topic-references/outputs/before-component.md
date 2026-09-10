本批只整理 `ChoicePanel` 这个组件单元，保持原有 `items`、`onSelect`、空态中文和主题背景行为。按给定规则，将原 `ChoicePanel.tsx` 中已有的类型、固定文案和样式移到本单元对应文件；不扩展订单入口、聊天入口或 `CellList` 的功能。

下面路径是合成工程的文件方案。实际工程的源码根、依赖导入路径与已有公开出口仍须核对；此处复用题设确认的 `CellList` 和 `useColors`，没有新增 SDK API。

```text
components/
├── ChoicePanel/
│   ├── ChoicePanel.tsx  # 修改：组合已有 CellList，移除无消费者的 selected
│   ├── types.ts         # 从原文件移入 props 与条目结构
│   ├── constants.ts     # 从原文件移入 EMPTY_MESSAGE
│   ├── styles.ts        # 从原文件移入主题样式工厂
│   └── index.ts         # 本单元的小型公开入口；已有时复用
└── CellList/
    └── index.ts         # 已有公开入口，本批不修改
```

树中只列本批文件及直接依赖的公开入口，不表示删除 `CellList` 的其他现有文件。对应渲染测试沿用工程已有位置；消费者现有导入如需调整，只定向指向 `ChoicePanel` 的公开入口。

`components/ChoicePanel/types.ts`：

```ts
export interface ChoicePanelItem {
  id: string;
  title: string;
}

export interface ChoicePanelProps {
  items: readonly ChoicePanelItem[];
  onSelect: (id: string) => void;
}
```

这些是面板的展示契约，放在所属组件。`ChoicePanelItem` 表示可选择条目，不引入客户业务模型，也不放到全局 `src/types/customer.ts`。

`components/ChoicePanel/constants.ts`：

```ts
export const EMPTY_MESSAGE = '暂无选项';
```

`EMPTY_MESSAGE` 是已经存在且有展示含义的命名固定值，迁移后中文内容不变。数组长度与 `0` 的比较直接保留，无需另设常量。

`components/ChoicePanel/styles.ts`：

```ts
import { StyleSheet } from 'react-native';
import type { useColors } from '@unif/react-native-design';

export function createStyles(colors: ReturnType<typeof useColors>) {
  return StyleSheet.create({
    root: {
      backgroundColor: colors.background,
    },
  });
}
```

主题输入类型从题设确认的公开 hook 派生，不复制一套设计系统颜色类型。样式工厂放在 `styles.ts`，当前主题颜色仍由组件调用 hook 后传入；不在模块级调用 hook，也不把本次渲染的样式对象当作固定常量共享。

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
  const styles = createStyles(colors);

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

`visibleItems` 依赖当前 props，`colors` 和 `styles` 依赖当前渲染，继续作为组件局部变量。删除无消费者的 `selected` 及不再需要的 `useRef` 导入，不新建 store 或 `variables.ts`。条目顺序、内容和选择回调原样交给现有 `CellList`，不增加筛选、缓存、确认或保存动作。React JSX 运行方式与实际导入写法沿用目标工程配置。

`components/ChoicePanel/index.ts`：

```ts
export { ChoicePanel } from './ChoicePanel';
```

订单选择弹层和聊天选择面板从这个小型入口使用组件。题设没有给出独立消费类型的需要，因此本方案不额外从公开入口导出 `ChoicePanelItem`、内部常量或样式工厂；`types.ts` 中的导出供本单元文件使用即可。落地时如已有被消费者使用的合法类型出口，应先核对并保留其兼容性。也不创建导出全部组件和内部类型的 `components/index.ts`。

不采用 `BaseButton` 建议：本批没有新增按钮交互，设计系统已有基础按钮时也应直接使用其公开入口。面板仅接收展示数据和回调；客户查询、选择协调与草稿保存继续归现有订单入口及所属业务交互负责，聊天展示不因此获得订单 store 或请求依赖。

`CellList` 没有自有命名固定值时，不需要 `constants.ts`。`styles.ts` 只在该单元确有样式定义时维护；`types.ts` 只承载实际存在的显式类型；`schema.ts` 由可执行边界校验的需要决定，本题没有这项需要；不生成统一的 `variables.ts`。本批不为了文件对齐修改 `CellList`，更不生成这些空文件。

验证范围如下，复用既有测试与工程命令：

- 组件渲染与交互：空数组仍显示“暂无选项”；非空条目正常展示；选择条目把对应 `id` 原样传给 `onSelect`；仅渲染不触发选择或业务写入。优先运行现有相关渲染测试，缺少这些行为断言时再补充。
- 主题与宿主：用组件实际需要的轻量主题宿主验证背景 token 及主题切换后的更新，不复制设计系统内部测试。
- 实际消费者：核对订单选择弹层与聊天选择面板的导入、props 接线和选择回调，运行受影响的组合测试，确认现有草稿处理仍由原业务链路执行。
- Web 预览：核对实际预览宿主对该组件入口及主题依赖的解析，执行对应编译或构建并检查空态和选择展示；原生渲染测试不能替代这项验证。
- 静态检查：使用现有 TypeScript、lint 与导入检查核对移位后的文件、类型兼容性、私有路径、循环依赖及公开出口。移除已无用途的导入，不把工程未提供的命令假定成可运行脚本。

本样本只完成了所给代码和规则的文本核对，未编辑真实工程、安装依赖或执行类型检查、测试、Web 构建、CI、真机验证，因此没有“测试通过”或“接入已完成”的结论。当前没有原生能力或平台实现变更，不因文件拆分默认要求整个领域测试或新增真机验证；若目标工程核对发现布局、手势、平台差异或其他消费者受到影响，再扩大验证范围。合并与发布仍以目标工程实际 required CI 为准。
