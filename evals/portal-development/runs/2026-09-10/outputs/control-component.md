本批只整理 `ChoicePanel` 单元，保留传入条目、点击后回调原始 id、空列表显示“暂无选项”和设计系统背景颜色的行为。按给定文件角色规则，把已有 props、命名文案和样式放回该单元的配套文件；这不扩大到其他组件或业务实现。订单入口继续负责查询客户、选择处理及保存草稿，聊天入口继续提供展示数据与回调。

本批文件树如下，`src/` 为给定规范中的源码根目录：

```text
src/components/
├── ChoicePanel/
│   ├── ChoicePanel.tsx     # 修改组件实现
│   ├── types.ts            # 现有 props 与展示条目接口
│   ├── constants.ts        # 现有中文空提示
│   ├── styles.ts           # 主题样式工厂
│   └── index.ts            # 小型公开入口；已有则按以下内容保持必要导出
└── CellList/
    └── index.ts            # 既有公开入口，本批不修改
```

`ChoicePanel.tsx`：

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

`types.ts`：

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

`constants.ts`：

```ts
export const EMPTY_MESSAGE = '暂无选项';
```

`styles.ts`：

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

`index.ts`：

```ts
export { ChoicePanel } from './ChoicePanel';
```

`useColors` 从规范明确的设计系统公开入口引用；`CellList` 从题设确认的具名公开入口引用。样式参数直接使用已确认 hook 返回类型的推导，没有另造 SDK 颜色接口。正式应用时需核对目标工程的模块解析、设计系统依赖版本及导出路径；本题没有读取或验证实际 SDK。页面和聊天使用 `ChoicePanel` 的单元公开入口，不深导入内部实现。题设没有消费者显式导入 props 或条目类型的需要，因此当前公共入口只导出组件；如目标工程已有这类实际公共类型消费者，应按其需要保留对应具名类型导出，而不是批量公开内部类型。

`colors`、`visibleItems` 和 `styles` 都取决于当前渲染，保留在组件调用内；`const` 不等于固定常量。无人消费的 `selected` ref 及其 `useRef` 导入删除，不创建其他状态、`variables.ts` 或 store。空数组长度的 `0` 判断保持内联。没有新增可执行校验契约，不创建 `schema.ts`。

不采用题设中的扩大修改建议：

- 不新增 `BaseButton`；本次没有按钮需求，设计系统已有的基础组件应通过公开入口复用。
- props 和展示条目类型留在 `ChoicePanel/types.ts`，不放全局 `src/types/customer.ts`，也不导入订单私有状态类型。
- `ChoicePanel` 不读取订单 store、不查询客户、不保存草稿，不接管场景确认规则。
- 不建立 `components/index.ts` 总出口，不从单元出口导出全部内部常量、样式、辅助函数或类型。
- `CellList` 没有自己的命名固定值就不补 `constants.ts`；其他角色文件也仅在有实际内容时存在，不为了与 `ChoicePanel` 对齐创建空的 `styles.ts`、`schema.ts` 或 `variables.ts`。本批不改动既有 `CellList`。

验证范围按实际影响限定：

1. 在目标工程运行既有 TypeScript、ESLint 及导入边界检查，核对 props 与 `CellList` 已有条目数组、回调契约兼容，检查公开入口解析、无业务层反向依赖和循环依赖。核对两个消费者及 Web 宿主中的静态导入，实际使用了深路径的消费者再同步调整其导入，不假设它们已经错误。
2. 复用对应组件既有渲染测试及其必要的轻量主题宿主，验证空列表中文提示逐字不变、有条目时按原顺序展示、选择回调携带对应 id，以及背景使用当前主题 token。主题变化后需继续获得更新的背景，不能因拆出样式成为共享静态值。按现有用例覆盖情况补充有缺口的行为断言，不复制设计系统或 `CellList` 内部测试。
3. 定向验证订单选择弹层与聊天选择面板的实际组合：数据仍由入口传入，点击动作仍交给原回调，订单原有处理链路接线没有中断，组件没有新增查询或保存副作用。测试路径在目标工程中定位，题设未提供具体文件名，不能声称已运行某个测试路径。
4. 核对 `website/` Web 预览宿主对单元入口、样式和设计系统依赖的解析，执行其已有相关编译或预览检查，查看空态、条目和点击交互。原生渲染测试不能证明 Web 接入正确。本批没有新增平台差异，不生成空 `.web.tsx` 或原生适配文件。

这是合成工程的书面修改方案：仅按提供规范核对代码组织与行为，未安装依赖、运行编译或测试、访问 SDK 或业务系统，也未声称设备验证或 CI 通过。实施时以目标工程真实脚本和上述消费者证据完成定向验证；系统合并和发布仍执行工程既定 CI，无需仅因文件拆分默认重跑整个领域测试。
