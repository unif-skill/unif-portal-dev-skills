# 原生鸿蒙 Icons

先读原生宿主的依赖声明与锁文件。采用同仓 Icons 时，按模块清单、公开导出和实际资源核对。采用已分发 HAR 时，按包版本和归档内容核对。

| 任务 | 所属资料 |
|---|---|
| 接入用法与包版本 | 实际采用模块或已安装 HAR 内的 `README.md`、`oh-package.json5`，以及宿主依赖声明和锁文件 |
| 原生参数与公开导出 | 包清单指定的公开入口及配套声明；已发布 HAR 可提供 `Index.d.ets`，沿其导出核对组件声明 |
| SVG 源、命名与生成 | RN Icons 的[同源生成与跨仓校验](https://github.com/unif-design/react-native-icons/blob/main/docs/DEVELOPMENT.md#同源生成与跨仓校验)，以及其中指定的生成器和实际鸿蒙源码目标 |
| 项目契约与目标验收 | [鸿蒙 Icons 规范](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-icons.md)；包内规范见[对应章节](harmony/icons.md#4-验证与采用) |

宿主可用的参数和资源以实际采用的包为准。仅有已安装 HAR 时可核对公开消费；生成校验和手写渲染维护还需取得对应的原生源码工程。

## 应用消费

从包根核对 UnifIcon、UnifIconName 与命名组件。当前原生参数包括 iconName、iconSize、iconColor、lineWidth 和 accessibilityLabel，命名组件不再传 iconName；不把 RN 的 size、color 等属性直接用于 ArkUI。颜色、尺寸由消费者按场景提供，不引入 Design 或应用字号状态来驱动图标内部。

装饰图标不产生重复读屏节点，真实操作由父控件提供名称、焦点、触摸面积和禁用语义；有独立语义时按原生 API 提供可访问说明。普通消费不运行生成器，不深导入 generated，不复制 SVG 或引入 RN 运行时。

## 源维护与验证

图形和命名沿 RN Icons 唯一 SVG 源、清单及生成器维护；从实际库 README 取得生成与两端校验入口，不手改 Index.ets、generated 或溯源清单。参数、原生渲染或无障碍行为在所属手写实现核对，生成资源不能代替平台行为迁移。同步范围遵守本次授权，单端修改不自动授权另一仓写入。

验证采用版本的真实 example 和独立 HAR 消费者，核对图形、参数更新、视口、颜色、读屏及父控件交互。来源一致、自动化、HAR 构建、设备效果与发布后安装分别取得证据；不从构建通过推断设备表现。
