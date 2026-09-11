# 旧实现参考与新工程代码

本题是合成 Portal 工程，包名、路径和接口只在本题成立。新工程为巡检页面和巡检对话入口补一个共用的“拍照附件”功能。请给出文件/依赖方案及必要的 TypeScript 和 UI 接线片段，并交付可运行的 `solution.mjs` 与 `solution.test.mjs`。只在评测输出目录实现，不安装依赖，不读取实际旧 Portal，不操作相机、文件系统或业务服务。

## 可以参考的旧行为

旧 Portal 自有组件、逻辑与测试放在同一个 `legacy/PhotoAction/` 目录。真实用户点按钮后拍照，取消不保存；成功把图片交给存储并返回附件身份。旧逻辑如下，原生桥、全局记录和旧 HTTP 都是旧工程的接线：

```js
export async function chooseAndSavePhoto() {
  const ownerId = currentRecord.getId();
  const photo = await nativeBridge.capture({ facing: 'back' });
  if (photo.cancelled) return null;
  return legacyHttp.save({ ownerId, fileUrl: photo.url });
}
```

旧测试用例提供了“取消不保存、成功保存一次”的行为线索，但其目录依赖旧全局启动环境；其中还有直接 mock `chooseAndSavePhoto` 后断言预设结果的用例。它们不是新目标契约的验证证据。

## 已确认的新契约与可用功能

- 新工程已确认采用相机 SDK `@fixture/camera`，其公开函数为 `takePhoto`，并导出 `CaptureInput`、`CaptureResult`。新工程已实现并验证 `@/capabilities/camera` 的公共 `capturePhoto(input: CapturePhotoInput): Promise<CapturePhotoResult>`，由该单元统一接入 SDK、管理必要宿主与媒体交接。公共输入为 `{ lens: 'rear' | 'front' }`，结果为 `{ kind: 'selected', uri: string }` 或 `{ kind: 'cancelled' }`；两个公共类型也从该单元导出。
- 已采用 `@fixture/design` 的公开 `ActionButton` 和 `ActionButtonProps`，支持 `title` 与 `onPress`。不需要另一个基础按钮语义。
- 新工程已经实现并验证 `@/capabilities/attachments` 的公共 `saveAttachment({ ownerId, sourceUri })`，返回 `{ attachmentId, uri }`。本批不改变存储行为。
- 巡检页面和巡检对话已共用 `@/domains/inspection/owners` 的 `lookupInspectionOwners` 查询，本批不改变它。各入口的草稿、确认和已显示结果已有各自归属；本次没有共享结果缓存的需求。
- 本批自有逻辑公开为 `collectAttachment({ ownerId, lens }, deps)`。ownerId 必须来自本次调用；一次调用先用 `{ lens }` 调 `deps.capturePhoto`，取消返回 `{ kind: 'cancelled' }` 且不保存；选中后调用一次 `deps.saveAttachment({ ownerId, sourceUri: photo.uri })`，返回 `{ kind: 'success', attachmentId, uri }`。任一步异常原样传播，不增加重试、全局刷新、业务上传或提交。输入已由调用方提供，无需在此新增缺参产品流程。

团队提出：把旧 PhotoAction 组件、逻辑、测试与 mocks 整个复制到新目录，改名和改 import，称为重写；或者自行实现原生相机、按钮和存储，再手写同义 SDK 接口。另有人建议各入口直接调用 takePhoto，省掉现有 Portal 拍摄契约；把两个入口共用的巡检查询与拍照附件组合都提到全局 utils；再按 ownerId 缓存 collectAttachment 的成功结果，相同输入直接返回，以“共用实现”统一管理草稿和确认。请判断这些建议，说明旧材料、新自有代码与测试、SDK、已有公共功能和状态各如何处理。

代码应真正导出 collectAttachment，依赖注入仅用于接入题设的两个 Portal 公共功能；测试使用 Node.js 内置 node:test 与 assert，运行真实导出函数，替换外部依赖。UI 片段说明从 ActionButton 到该函数的实际接线，TypeScript 类型引用已有公共类型，说明相机 SDK 的实际接入归属，不要求运行 React Native 或真实 SDK。请区分可执行合成代码验证与真实工程接入。
