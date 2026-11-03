# 原生鸿蒙 HMS Scan

先核对 [harmony-hms-scan README](https://github.com/unif-design/harmony-hms-scan/blob/main/README.md)、[包清单](https://github.com/unif-design/harmony-hms-scan/blob/main/library/oh-package.json5)和 main 入口；[目标契约](https://github.com/unif-design/unif-platform-architecture/blob/main/libraries/harmony-hms-scan.md)规定识别、交互与资源交接。本地按同一相对路径读取，真实 ArkTS 和 Scan Kit 签名按采用版本确认。

若当前仍为空 HAR 或 `export {};`，没有可供接入的扫码组件或解码函数。只核对契约与缺口，不把 RN Scanner、HmsScanView、decodeImage 改包名作为原生 API，也不因技能覆盖而恢复暂停的功能开发。

## 目标边界

实时预览、图片解码、权限与结果映射分别核对，低层能力不依赖完整扫码 UI。选图由外部提供；图片解码不因复用扫码界面而自动申请相机权限、打开相机或下载文件。

保留原始码值、码制、实际元数据和过滤语义；有效空结果与无效响应、SDK 错误分开。识别后的选用只交付结果，商品／客户含义、URL 打开和业务确认归应用。手电按实际设备状态反馈。

取消、重扫或宿主结束停止旧结果采用，不等于底层读取结束。借用图片由提供方拥有，等 SDK 真正结束读取后交回本次占用；库只清理自己拥有的副本。迟到选图、旧回调和旧释放不能处理新文件。

## 实施与验证

有开发授权时按所属仓库入口、有效契约和真实 SDK 组织实现，保留权限重读、格式过滤、返回／重扫／选用及可访问性。平台与厂商选择沿项目约定，不因 Scan Kit 示例改变地图或分享提供方。

自动化、HAR 构建、设备相机／码样／相册／手电／权限及业务回包分别验证。空包构建和图片解码测试不证明实时扫码交互或相机拍摄已完成。
