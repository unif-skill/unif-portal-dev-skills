# 原生鸿蒙 Icons

先核对采用的 `@unif/harmony-icons` 版本、HAR 公开声明及实际实现。库版本从 library/oh-package.json5 取得，不能用 RN 当前版本或 Node 工具版本代替；中心仓发布、审核和安装状态另行确认。

| 任务 | 所属资料 |
|---|---|
| 消费、同源生成与验证 | [仓库 README](https://github.com/unif-design/harmony-icons/blob/main/README.md)、[包说明](https://github.com/unif-design/harmony-icons/blob/main/library/README.md) |
| 原生参数与渲染 | [docs/API.md](https://github.com/unif-design/harmony-icons/blob/main/docs/API.md)、[UnifIcon.ets](https://github.com/unif-design/harmony-icons/blob/main/library/src/main/ets/UnifIcon.ets) |
| 实际公开入口与版本 | [Index.ets](https://github.com/unif-design/harmony-icons/blob/main/library/Index.ets)、[包清单](https://github.com/unif-design/harmony-icons/blob/main/library/oh-package.json5) |
| 项目契约与目标验收 | [鸿蒙 Icons 规范](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-icons.md)；包内规范见[对应章节](harmony/icons.md#4-验证与采用) |

本地按相同相对路径读取；接口按采用修订核对，规范链接用于定位，目标契约不代替实际公开声明。

## 应用消费

从包根核对 UnifIcon、UnifIconName 与命名组件。当前原生参数包括 iconName、iconSize、iconColor、lineWidth 和 accessibilityLabel，命名组件不再传 iconName；不把 RN 的 size、color 等属性直接用于 ArkUI。颜色、尺寸由消费者按场景提供，不引入 Design 或应用字号状态来驱动图标内部。

装饰图标不产生重复读屏节点，真实操作由父控件提供名称、焦点、触摸面积和禁用语义；有独立语义时按原生 API 提供可访问说明。普通消费不运行生成器，不深导入 generated，不复制 SVG 或引入 RN 运行时。

## 源维护与验证

图形和命名沿 RN Icons 唯一 SVG 源、清单及生成器维护；从实际库 README 取得生成与两端校验入口，不手改 Index.ets、generated 或溯源清单。参数、原生渲染或无障碍行为在所属手写实现核对，生成资源不能代替平台行为迁移。同步范围遵守本次授权，单端修改不自动授权另一仓写入。

验证采用版本的真实 example 和独立 HAR 消费者，核对图形、参数更新、视口、颜色、读屏及父控件交互。来源一致、自动化、HAR 构建、设备效果与发布后安装分别取得证据；不从构建通过推断设备表现。
