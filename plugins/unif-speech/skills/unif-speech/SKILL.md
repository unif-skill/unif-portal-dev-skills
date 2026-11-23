---
name: unif-speech
description: 接入 @unif/react-native-speech 的音频采集、临时凭证和实时识别，排查语音输入结果和麦克风释放。语音合成及其他语音 SDK 另查对应接口。
metadata:
  package: "@unif/react-native-speech"
---

# Unif Speech

## 按需要选择入口

先查应用锁定版本的 `package.json` 根入口和子路径导出。本地资料在 `docs`，官网索引标明构建版本。[文档与版本索引](https://unif-design.github.io/react-native-speech/llms.txt)

| 用途 | 子路径 | 公开入口 |
|---|---|---|
| 音频采集 | `/capture` | [openAudioCapture](https://unif-design.github.io/react-native-speech/md/api/capture.md) |
| 临时凭证 | `/credentials` | [createSpeechCredentialAccess](https://unif-design.github.io/react-native-speech/md/api/credentials.md) |
| 实时识别 | `/realtime` | [openSpeechSession](https://unif-design.github.io/react-native-speech/md/api/realtime.md) |
| 语音输入框 | `/input` | [useVoiceInput](https://unif-design.github.io/react-native-speech/md/api/input.md) |

应用提供权限、身份、HTTP 换发、业务词表和输入界面，持有草稿并负责发送。采集只交付缓冲区中的实际 PCM，录音文件和识别连接由调用方管理。遇到格式不匹配时返回实际错误，避免隐式重采样。

凭证访问实例属于当前身份，单次取消保留其他有效缓存。按协议交付凭证，避免凭据出现在 URL 或日志中。普通断网按实际失败处理，避免自动换发或重连。身份结束时关闭所属会话并释放凭证实例。

## 文字结果与麦克风释放

- **文字是否能写入草稿**　`transcript` 供当前界面展示，草稿采用本轮 `onResult` 的确认或未确认文字，失败时可用 `finalText`，取消保留原草稿。`context_ended` 和卸载静默结束本轮，停止向旧接收方交付。
- **麦克风能否开始下一轮**　核对同一轮的 `finish`、`close` 和原生停止结果。识别超时、停止采用文字或收到取消通知后，仍需等待旧采集实际释放才能重新开始。旧回调只处理所属轮次。[结果采用与释放时序](references/workflows.md)

维护时从异常所属的采集、会话或输入 Hook 追到真实消费者，再核对宿主实际编译的音频 SDK 与补丁。麦克风释放在设备上验证，厂商识别结果看服务端终态。[原生接线与补丁](https://unif-design.github.io/react-native-speech/md/native-setup.md)
