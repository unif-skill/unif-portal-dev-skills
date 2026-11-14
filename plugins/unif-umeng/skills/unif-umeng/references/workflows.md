# 初始化、分享与统计

## 初始化

核对实际采用版本的配置字段、初始化不可变语义与原生回调接线。应用拥有同意记录和调用时机；仅使用统计时按公开契约提供必要配置。初始化中的并发、配置锁定、失败恢复和厂商副作用以本库公共契约为准，不通过重复初始化或自造 preInit 入口绕过。

## 分享

- 已有目标和 `ShareContent` 时直接调用 `share({ target, content })`。
- 内容已备好、需要 SDK 展示渠道时，在当前窗口挂载 `useShareSheet()` 返回的宿主，用同一实例的 `controller.open(content)` 打开面板。普通页面和模态窗口分别使用各自的实例。
- `@unif/react-native-umeng` 2.7.0 起可在页面内先选渠道。应用调用 `getShareTargets()`，将成功返回的 `targets` 交给 `SharePanel`，查询失败则展示具体错误。收到 `onSelect(target)` 后才按需截图、上传并准备内容。准备期间防止重复进入并设置 `disabled`。以长图为例，取得有效图片 URL 后才用原目标调用 `share`。选前关闭、准备失败或准备已取消时均不发起分享。

内容和业务身份属于本次调用快照。SDK 开始前可以取消选择。开始后关闭面板、触发 signal 或卸载宿主只结束呈现，由原调用接收 SDK 结果，应用按原场景决定是否采用。文件保留至实际读取结束，例如上传接管截图后按上传方的释放通知清理。SDK 的 `success` 只证明本次分享取得成功回执。

## 维护与验证

从 docs/DEVELOPMENT.md、src/index.ts、package.json、common/share/analytics 及相关原生实现定位变更；目标契约为任务采用规范根的 libraries/react-native-umeng.md。

核对真实消费者、初始化前/失败状态、在途 busy、同实例呈现、原调用回执及统计参数。保留初始化失败、取消和不可判断副作用的错误，不将它们补成成功。

本库 Mock 只替代外部边界。原生链接、URL/Universal Link/Activity 回调、实际第三方应用、取消及统计平台回执分别验证；Web unsupported、单测和打包通过均不替代设备或真实平台结果。
