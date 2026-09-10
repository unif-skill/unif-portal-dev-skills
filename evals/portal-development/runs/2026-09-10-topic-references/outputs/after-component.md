本批只整理 `ChoicePanel` 单元及其必要配套文件，保留原来的 props、中文空态、主题背景和选择回调。订单入口继续负责查询客户、处理选择和保存草稿；页面与聊天都通过同一个组件公开入口复用面板。

这里的“只修改 ChoicePanel”限定业务范围。按照提供的文件规则，其现有显式类型、命名固定值和样式分别落到本单元的角色文件；不会把其他组件按模板补齐一遍。

本批目标文件树如下。配套文件若已存在，就合并到对应文件，保留无关内容；若不存在，则创建有实际内容的文件。

```text
components/
├── CellList/
│   └── index.ts               # 已有公开入口，本批不修改
└── ChoicePanel/
    ├── ChoicePanel.tsx        # 展示与事件转交
    ├── types.ts               # 本组件的展示条目与 props
    ├── constants.ts           # 原有中文空态固定值
    ├── styles.ts              # 接收当前主题颜色的样式工厂
    └── index.ts               # 小型公开入口
```

下列代码采用材料明确的设计系统公开入口与 `useColors` 导出名，`CellList` 从题设已有的 `components/CellList/index.ts` 导入。实际工程接线时仍需核对依赖版本、路径解析和 JSX 配置，未假设额外的 SDK 类型或 API。

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

展示数据归组件自身所有，不命名成客户 DTO，也不迁到全局 `src/types/customer.ts`。入口可将自己的业务数据投影为这个展示结构。

`components/ChoicePanel/constants.ts`：

```ts
export const EMPTY_MESSAGE = '暂无选项';
```

`components/ChoicePanel/styles.ts`：

```ts
import type { useColors } from '@unif/react-native-design';
import { StyleSheet } from 'react-native';

export function createStyles(colors: ReturnType<typeof useColors>) {
  return StyleSheet.create({
    root: {
      backgroundColor: colors.background,
    },
  });
}
```

样式输入类型直接从已确认的公开 hook 推导，不另造颜色接口。颜色取值仍由组件每次渲染时传入；工厂保持原样式生成方式，不在模块级缓存当前主题或复制 token。

`components/ChoicePanel/ChoicePanel.tsx`：

```tsx
import { useColors } from '@unif/react-native-design';
import { Text, View } from 'react-native';

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

`visibleItems`、`colors` 和生成的 `styles` 都依赖当前调用，留在组件作用域。没有消费者的 `selected` 与相应 `useRef` 导入直接移除。空数组判断中的 `0` 无需抽成常量；这里也不新增过滤、排序、选中状态、确认或保存行为。

`components/ChoicePanel/index.ts`：

```ts
export { ChoicePanel } from './ChoicePanel';
```

本题已知的外部消费者只需组件入口，因此公共 `index.ts` 不额外导出条目类型、常量和样式工厂。`types.ts` 中的具名导出供本单元协作使用；若目标工程实际存在直接使用 props 类型的消费者，应按引用证据显式保留所需公共类型出口。订单选择弹层、聊天选择面板和 Web 预览接线时核对其导入，确需调整的只改为此单元入口；题目没有提供这些文件的真实路径，因此不编造文件名或别名。

不采用建议中的 `BaseButton`、业务 store 依赖、客户查询或总 `components/index.ts`。当前面板已有明确的组合用途，基础 UI 继续使用设计系统，列表组合使用 `CellList` 公开入口。将所有组件及内部类型聚合导出会扩大公共面和依赖范围，本批没有这个需求。

`CellList` **不需要补齐空文件**。它没有自己的命名固定值，就不创建 `constants.ts`；其他角色文件也仅在具有实际内容时存在。不能因 `ChoicePanel` 有这些文件，就给 `CellList` 生成空的 `styles.ts`、`schema.ts` 或 `variables.ts`。本批没有新的可执行边界校验需求，不引入 Schema；局部变量也不集中到 `variables.ts`。

验证范围按现有测试和三个真实消费者确定：

1. 运行既有组件渲染测试，确认空数组仍显示“暂无选项”，非空数组仍交给 `CellList` 展示；选择条目时原样传递对应 `id`，不新增调用次数或副作用。仅当现有断言缺失这些行为时补充相应断言，不复制设计系统或 `CellList` 自身的内部测试。
2. 使用组件实际需要的轻量主题宿主，核对根背景来自当前主题，并验证主题切换后更新。运行目标工程现有 TypeScript、lint 与导入检查，检查拆分后的类型、具名导出、路径、无用导入和循环依赖。
3. 定向运行订单选择弹层与聊天选择面板的相关组合用例：条目和回调接线保持有效，订单入口原有选择与草稿处理不因组件整理改变。通过真实静态引用定位需要调整的导入；若找到其他消费者，再按实际影响扩展验证。
4. 核对并验证 Web 预览的实际接入、空态和选择交互，检查主题显示。保留当前跨平台实现；没有实际平台差异依据时不生成空的 `.web.tsx`。本批未改原生 SDK 或配置，不以此为由增加全量原生构建或整个业务领域的测试。

已完成的是对题设代码、技能文件规则、UI 边界、依赖出口与定向验证要求的文本核对，以及上述方案和代码编写。本次没有读取或修改真实工程，没有安装依赖，也没有运行类型检查、渲染测试、Web 预览或 CI，因此不声称这些验证已经通过。真实交付时执行目标工程已有的相关检查与合并门禁，并分别报告结果。
