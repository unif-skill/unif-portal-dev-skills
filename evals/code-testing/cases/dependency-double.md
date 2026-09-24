# 外部依赖替身与真实边界

以下是独立的合成适配任务。`vendor.mjs` 表示工程已锁定版本的实际依赖行为，`adapter.mjs` 是本次被测实现；代码片段均为完整题设，不代表真实项目或 SDK。只给出最小修复、测试调整和实际可证明的验证，不修改业务仓库。

`vendor.mjs`：

```js
export class Decoder {
  initialize(config) {
    if (!config || config.sampleRate !== 48000) throw new Error('configuration required');
    this.ready = true;
  }
  decode(value) {
    if (!this.ready) throw new Error('not initialized');
    return value;
  }
}
```

`adapter.mjs`：

```js
export function decodeWith(vendor, value) {
  const decoder = new vendor.Decoder();
  decoder.initialize();
  return decoder.decode(value);
}
```

现有测试把依赖替换为 `{ Decoder: class { initialize() {} decode(value) { return value; } } }`，断言返回原值，测试为绿。团队准备直接交付，称“替身已经覆盖依赖接口，真实依赖只需留给以后设备测试”。请根据已给契约决定当前结果能证明什么、应修改哪里，并提出会让错误调用失败的最小验证。不要把替身测试、真实依赖调用、平台构建和设备验收混为一项。
