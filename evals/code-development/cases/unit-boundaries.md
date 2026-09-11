# 页面与组件的单元组织

以下是三个独立的合成 Portal 客户端任务，采用本次提供的工程规范与技能入口。文件、API 和测试结果均为题设，不代表实际工程。只输出各任务的文件组织、必要的导入或出口及判断依据，不安装依赖、不写入工程、不执行 Git 或外部操作。已有功能契约完整，行为不变。

## A：新增联系人页面

`app/contacts` 已提供公开的联系人查询和编辑接口。本批新增 `ContactListScreen` 与 `ContactEditScreen`，前者有搜索输入和选中状态，后者有表单草稿；两页各自有 props、主题样式和固定展示文案，分别注册为页面入口。

两页都会显示 `ContactAvatar`，它通过 props 接收图片和名称，仅维护图片加载状态。编辑页的 `ContactForm` 通过 props 接收字段和编辑事件，有自身的 props、样式及校验提示常量，只有编辑页使用。列表页含具名 React 组件 `CountLabel`，接收数字并返回一段 JSX，没有单独的样式、命名常量或显式类型声明；它只在列表页使用。列表的 `renderItem` 是传给现有列表组件的渲染回调。

本功能尚无页面目录；工程其他已实现页面采用 `screens/` 分类。请给出本批文件树及公开入口，说明页面、共享组件、私有组件、渲染回调和配套文件的归属。

## B：审查已完成的偏好页面

本次新增 `app/preferences/screens/DisplayScreen.tsx` 和 `NotificationScreen.tsx`，分别是两个已注册页面。`screens/types.ts` 同时定义两页互不相关的 props；`screens/styles.ts` 的同一工厂包含两页各自的布局；`screens/constants.ts` 收集两页的固定文案。

另有 `screens/PreferenceSummary/`，包含 `PreferenceSummary.tsx`、`types.ts`、`styles.ts` 和 `index.ts`。它不是页面，由两个页面通过 props 使用。`DisplayScreen.tsx` 内还有具名 React 组件 `PreviewTile`，通过 JSX 标签使用并维护局部展开状态；它的 props 与页面 props 放在同一 `types.ts`，主题样式也和页面混放。

任务计划曾把上述文件都安排到 `screens/`。现有 TypeScript、ESLint 和行为测试在题设中均已通过；ESLint 只检查显式类型声明位于 `types.ts`，没有检查单元或目录归属。

请审查这批文件组织，指出有依据的问题及修正范围，区分既有明确要求与需要进一步确定的组织选择。若接受某处现状，说明依据。列出文件移动后实际需要复核的消费者，不新增功能行为或另一轮完整设计。

## C：调整同一交互单元

`app/preferences/components/ChoiceCard/` 已有 `ChoiceCard.tsx`、`ChoiceMarker.tsx`、`types.ts`、`styles.ts` 和 `index.ts`。只有主组件供两个偏好页面使用；`ChoiceMarker` 是父单元私有展示组件，独立实现文件已有。它的参数直接引用设计系统公开类型，复用父单元已有样式，没有需独立维护的配套内容。

`ChoiceCard.tsx` 内还有普通格式函数和传给列表的 `renderItem` 回调。`app/preferences/selection` 拥有两页和 ChoiceCard 实际共用的公开 `SelectionOption` 契约，消费者从其公开入口导入；同一功能的默认选项由该功能的 `constants.ts` 维护。另有无显式类型或命名常量的普通单文件工具 `formatChoiceLabel.ts`。

本工程另有 `capabilities/imagePicker/PickerHost.tsx`，按已有能力契约承接选择会话与设备接线，目前只有偏好页面使用。有人建议因其只有一个页面消费者，将它移入该页面单元。

本批仅改 ChoiceCard 的间距与渲染回调中的展示文字。请确定改动范围，说明各文件、共享契约及公共出口是否需要调整，并给出对应验证范围。
