# 共用组件的本批修改

本题是采用 Portal 新架构的合成工程，不证明实际 SDK 或业务 API。只依据提供规则与以下事实，输出本批文件树、关键文件的 TypeScript/TSX 内容及验证范围；不用安装依赖或实现题设之外的功能。

工程已有 `components/CellList/index.ts` 的具名导出 `CellList`，其公开 props 接受条目数组与 `onSelect`；设计系统的公开 `useColors` 提供颜色 token。订单入口已负责查询客户、选择及保存草稿。现在仅修改 `components/ChoicePanel/ChoicePanel.tsx`，让页面与聊天都能复用选择面板，保持原交互与中文说明。以下为待整理代码：

```tsx
interface ChoicePanelProps {
  items: readonly { id: string; title: string }[];
  onSelect: (id: string) => void;
}
const EMPTY_MESSAGE = '暂无选项';
export function ChoicePanel(props: ChoicePanelProps) {
  const colors = useColors();
  const visibleItems = props.items;
  const selected = useRef<string | null>(null);
  const styles = StyleSheet.create({ root: { backgroundColor: colors.background } });
  return <View style={styles.root}>{visibleItems.length === 0
    ? <Text>{EMPTY_MESSAGE}</Text>
    : <CellList items={visibleItems} onSelect={props.onSelect} />}</View>;
}
```

实际导入路径除上述公开入口外按目标工程核对，本题允许用已确认导出名表达导入，不推造 SDK API。现有消费者是订单选择弹层与聊天中的选择面板，Web 预览也使用该组件；通用组件已有对应渲染测试。`selected` 已无消费者，可以移除。

有人建议新建 `BaseButton` 包装设计系统、把 props 放到全局 `src/types/customer.ts`，组件直接读取订单 store 并查询客户，统一生成空的 `constants.ts/styles.ts/schema.ts/variables.ts`。他还建议从 `components/index.ts` 导出所有组件及所有内部类型，以方便导入。请给出最终修改，并说明已有 `CellList` 没有自有固定值时是否也要补齐这些文件。
