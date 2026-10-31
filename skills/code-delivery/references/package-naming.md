# Unif RN 库包身份

本专题和[组织资产](../assets/organization.json)适用于 `unif-design` 组织的 React Native 库。npm 包名遵循资产的 namePattern，例如 `@unif/react-native-camera`；具体名称由已确认能力及本库 package.json 决定，不将现有六库作为未来库的封闭清单。

新库核对仓库、package.json、公开入口、构建产物及发布注册表的同一包身份。首次／恢复发布同时核对已有版本和历史占用；一次 404 或空版本列表不能否定已确认的发布历史。

原生鸿蒙 HAR、后端和其他工程使用自身包清单与发布契约，不套用 RN 名称模式。实际消费者的导入、依赖范围与锁定版本来自各工程；改名或迁移不能仅通过本地 manifest 推断已完成。
