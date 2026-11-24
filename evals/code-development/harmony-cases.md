# 原生鸿蒙与 RN 平台选择样本

仅向被测上下文提供本文件的请求、工程素材、所选技能包和规范源；不提供评分、前一次输出或预期答案。每例只输出实施摘要，不修改源码、构建、安装、联网或执行真实业务。

## native-libraries

为纯原生 HarmonyOS 7 API 26 的 Unif 新建六个 @unif/harmony-* 库，先做 icons 和 design；对应 RN 库已有 SVG 清单、colors.ts、React 组件和 Hooks。请确定这次开发应采用的技能、规范和工程组织，列出首批文件职责及验证方式。这里只输出实施摘要，不修改仓库。

```json
{
  "target": {
    "kind": "ArkTS/ArkUI",
    "targetSdkVersion": "26.0.0",
    "compatibleSdkVersion": "26.0.0"
  },
  "libraryNames": [
    "icons",
    "design",
    "chat",
    "camera",
    "hms-scan",
    "umeng"
  ]
}
```

## rn-only

只修 RN 的 IconButton 在大字号下文字与图标垂直偏移，调用方已经传入正确字号。请给出核查与修改范围、所用技能及验证方式。这里只输出实施摘要，不修改仓库。

```json
{
  "target": "@unif/react-native-design",
  "currentContract": "字体只缩放一次，图标位置跟随现有布局；尺寸与交互保持",
  "workspaceAlsoContains": "ai-app-portal-harmony"
}
```

## shared-ts

这些 .ts 文件可以一起封成 @unif/utils 给 RN 和纯原生鸿蒙用吗？请判断每个文件的处理方式，以及共享库要怎样验收。这里只输出实施摘要，不修改仓库。

```json
{
  "clamp.ts": "export function clamp(v: number, lo: number, hi: number): number { return Math.max(lo, Math.min(v, hi)); }",
  "scale.ts": "import { Platform } from 'react-native'; export const scale = Platform.OS === 'ios' ? 1 : 0.95;",
  "isUrl.ts": "export function isUrl(value: string): boolean { return new URL(value).protocol === 'https:'; }",
  "colors.ts": "export const BRAND_ORANGE = '#EB6E00';"
}
```

## native-scan-and-evidence

给纯 ArkUI 页面添加扫码：只借用传入的图片文件，取消不返回成功；我们已有 unif-hms-scan 技能。API 26 工程已打出未签名 HAP，可以说扫码完成了吗？请给出实施范围、依据和结论。这里只输出实施摘要，不修改仓库。

```json
{
  "nativeScanImplementation": "尚未接入",
  "rnLibrary": "@unif/react-native-hms-scan",
  "deviceEvidence": null
}
```

## native-glass

鸿蒙 design 的卡片和顶部导航要保持现有 Unif 玻璃界面，大字号、深色和系统降低材质效果时也要能用。请确定材质采用与验收办法；目前只有本地构建通过。这里只输出实施摘要，不修改仓库。

```json
{
  "targetSdkVersion": "26.0.0",
  "reference": "现有 RN 布局、内容、入口与操作保持",
  "deviceEvidence": null
}
```

## identity-and-h5

原生鸿蒙登录及聊天附件接线时，用户切换账号后旧上传响应才回来，H5 仍提供现有业务页面。同次整理账号回执与营销请求时，有评审建议为下单禁用 HTTP 401 后的重试。请根据工程采用的 RN 和现有目录，确定应保留的行为、常量与类型的归属，以及两端怎么验收。这里只输出实施摘要，不修改仓库。

```json
{
  "login": "既有业务账号、角色与设备校验",
  "h5": "既有业务与桥接协议",
  "file": "上传期间页面可能关闭，不能误删已交付文件",
  "adoptedRN": {
    "version": "4.1.14",
    "revision": "fixture-adopted",
    "orderPath": "下单通过 Bearer 会话请求提交",
    "session": "当前身份收到 HTTP 401，刷新成功后原请求只重试一次；业务码 1003 直接结束原会话"
  },
  "harmonyAccount": "AccountReply.ets 混有业务文案常量、跨模块回执类型和解析函数，同目录已有 constants.ets 与 types.ets。聊天附件已有独立实现，但平铺在 chat/，常量文件名为 PortalAgentAttachmentConstants.ets"
}
```

下列两个定向样本用于补充库文档路由和共同字段消费者检查；不与先前三组的六例运行混作同一轮。

## native-library-docs

为 @unif/harmony-design 的 Button 增加库使用文档与公开示例，页面上展示 API 说明和真实原生演示入口。当前库是纯 ArkTS/ArkUI 的 API 26 HAR，已经有通过公开导出消费的示例 HAP。请按所提供技能给出资料选择、实施范围和验收方法，不修改代码。

```json
{
  "platform": "HarmonyOS 7 / API 26",
  "package": "@unif/harmony-design",
  "publicEntry": "Index.ets",
  "example": "已有 ArkUI 示例 HAP",
  "website": "尚未选择站点实现工具",
  "rnLibraries": "本次不修改"
}
```

## shared-contract-change

共同聊天附件功能新增文件大小显示，服务端契约已加入可选 sizeBytes，RN 已接入，鸿蒙还未接入。请说明还需核对哪些生产方、消费者和验证，是否能标记共同功能完成。这里只给实施摘要，不修改代码。

```json
{
  "source": "服务端单一附件 Schema，由该源生成客户端契约",
  "field": {
    "name": "sizeBytes",
    "meaning": "可选非负整数字节数；不改变上传请求、权限或结果成功条件"
  },
  "consumers": {
    "rnChat": "已接入",
    "harmonyChat": "未接入",
    "orderFlow": "不读取该字段"
  },
  "target": "RN 与纯原生 HarmonyOS 7 API 26 的同一 Unif 产品"
}
```
