---
name: unif-speech
description: 在查询、接入、维护或排查 @unif/react-native-speech 的音频采集、临时凭证、实时识别会话、语音输入及麦克风收尾时使用。不用于语音合成或其他语音 SDK。
metadata:
  package: "@unif/react-native-speech"
---

# Unif Speech

先核对实际版本、锁文件及 package.json 的根入口与子路径导出。[官网索引](https://unif-design.github.io/react-native-speech/llms.txt) 不代表已安装版本；资料与依赖不一致时取得对应包或已核实修订的公开类型。

## 按任务读取

本地资料在 docs，website/docs 链接到同一来源；按实际层次读取，避免为单项接口接入整套流程。

| 能力与公开入口 | 资料 |
|---|---|
| 宿主组合与权限 | [快速开始](https://unif-design.github.io/react-native-speech/md/quick-start.md) |
| `/capture`：openAudioCapture | [音频采集](https://unif-design.github.io/react-native-speech/md/api/capture.md) |
| `/credentials`：createSpeechCredentialAccess | [临时凭证](https://unif-design.github.io/react-native-speech/md/api/credentials.md) |
| `/realtime`：openSpeechSession | [实时识别](https://unif-design.github.io/react-native-speech/md/api/realtime.md) |
| `/input`：useVoiceInput | [语音输入](https://unif-design.github.io/react-native-speech/md/api/input.md) |
| Expo Modules、音频补丁与实际包消费 | [原生接线](https://unif-design.github.io/react-native-speech/md/native-setup.md) |

## 使用边界

应用持有权限、身份、HTTP 换发、业务词表、输入界面和草稿。低层采集不申请权限、不保存录音或连接识别服务；采用真实 PCM 格式，不以请求参数代替实际输出，也不在会话层新增隐式重采样。

凭证 access 属于当前身份范围，取消不清除其他有效缓存；身份结束时释放所属实例。鉴权通过当前公开协议交付，凭证不放入 URL 或日志；普通断网不自动换发或重连。

finish、close、停止采集和结果采用分别核对。停止文字采用或等待超时不能证明麦克风已释放。useVoiceInput 的 transcript 是本轮展示，text 的 confirmed／unconfirmed、failed 的 finalText 与 cancelled 按契约交付；草稿拼接和发送仍归应用。旧轮次不得影响新输入，context_ended 与卸载不回调旧接收方。

## 实施与验证

本技能独立可用，具体接入、源码与验证见[任务指引](references/workflows.md)。检查命令取当前工程。Web unsupported、Mock、SDK 补丁检查、实际包编译、设备麦克风与真实识别分别报告；查询接口不执行录音、联网识别或安装。
