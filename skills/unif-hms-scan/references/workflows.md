# 扫码接入与维护

## 选择已有能力

- 需要完整交互时先查 Scanner，包括权限、选图交接和退出回调；只定制取景时查 HmsScanView 的 props、事件与权限前置。
- 只识别图片时使用 decodeImage。输入按采用版本的 URI 契约准备；当前资料要求可读本地 file URI，其他相册 URI 由已有选图能力转换，不在扫码组件内另造文件系统。
- 多结果、未知格式和空数组保留各自语义。空数组仅表示本次 SDK 未交付结果，不能保证图片里没有码；错误不转换成空数组掩盖。

## 生命周期与状态

自行调用 decodeImage 时等待 Promise 结算再归还文件；交给 Scanner 时按 ScannerImage.onSourceReleased 的实际契约归还。选择器、页面退出、识别结束是不同的事件。

权限状态与 ScanError 从公共接口取得，不在应用重写平台映射。自定义相机在授权后启动；从设置返回只核对真实状态，不自动反复申请。torch 是请求，onTorchState 是实际状态；lowLight 与硬件 available 分开。

## 源码维护与验证

从 docs/DEVELOPMENT.md、src/index.tsx、package.json 和实际权限/解码/Scanner 实现定位变更；目标设计是所采用规范根的 libraries/react-native-hms-scan.md。维护采用工程指定规范；已配置相应技能时，可用 react-native-library 取得通用库规则，从 code-development 的“RN 项目采用”取得组织约定。

验证实际消费者的无结果、多结果、错误、取消、文件借用及视图重挂载；原生图片方向、角点坐标、解码预算、并发队列和权限变化分别核对所属实现。需要改这些行为时先保留现有输入校验和资源释放。

命令取实际 package.json 和 CI；JS/类型、Android/iOS 编译、设备识别/手电/权限以及 Web unsupported 分开报告。iOS 厂商切片是否支持模拟器按当前安装二进制确认，不用模拟器失败推断真机能力。
