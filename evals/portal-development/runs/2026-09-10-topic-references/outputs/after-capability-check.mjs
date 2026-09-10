import assert from 'node:assert/strict';

const DEFAULT_LIMIT = 1;
const READ_REASONS_SUCCESS_CODE = 200;
async function pickImage(input, sdk) {
  const controller = new AbortController();
  const chosen = new Map();
  const limit = input.limit ?? DEFAULT_LIMIT;
  const files = await sdk.pick({ limit, signal: controller.signal });
  files.forEach((uri, index) => chosen.set(uri, index));
  return Array.from(chosen.keys());
}
function asRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? value : undefined;
}
function readReasonOptions(data) {
  if (!Array.isArray(data)) return undefined;
  return Array.from(data, item => {
    const row = asRecord(item);
    return {
      id: typeof row?.id === 'string' ? row.id : undefined,
      label: typeof row?.name === 'string' ? row.name : undefined,
    };
  });
}
function adaptReasonsResponse(raw) {
  const envelope = asRecord(raw);
  const code = envelope?.code;
  if (code === READ_REASONS_SUCCESS_CODE) {
    return { kind: 'success', code, options: readReasonOptions(envelope?.data) };
  }
  return { kind: 'unconfirmed', code };
}

const seen = [];
const sdk = { async pick(input) { seen.push(input); return ['u2', 'u1', 'u2']; } };
assert.deepEqual(await pickImage({}, sdk), ['u2', 'u1']);
assert.equal(seen[0].limit, 1);
assert.equal(seen[0].signal.aborted, false);
await pickImage({limit: 3}, sdk);
assert.equal(seen[1].limit, 3);
await pickImage({limit: 0}, sdk);
assert.equal(seen[2].limit, 0);
assert.deepEqual(await pickImage({}, {async pick() {return [];}}), []);
const signals = [];
const concurrentSdk = { async pick({signal}) { signals.push(signal); const n = signals.length; await Promise.resolve(); return [`call-${n}`]; } };
assert.deepEqual(await Promise.all([pickImage({}, concurrentSdk), pickImage({}, concurrentSdk)]), [['call-1'], ['call-2']]);
assert.notEqual(signals[0], signals[1]);
const cancelled = new Error('SDK cancellation');
await assert.rejects(pickImage({}, {async pick() { throw cancelled; }}), error => error === cancelled);
assert.deepEqual(await pickImage({}, {async pick() {return ['sdk-b'];}}), ['sdk-b']);
const result = adaptReasonsResponse({code:200, data:[{id:'R1'},null,{id:'R2',name:'真实名称'},{id:'R2',name:'重复标识'}]});
assert.equal(result.kind, 'success');
assert.deepEqual(result.options, [{id:'R1',label:undefined},{id:undefined,label:undefined},{id:'R2',label:'真实名称'},{id:'R2',label:'重复标识'}]);
assert.deepEqual(adaptReasonsResponse({code:200,data:[]}).options, []);
assert.equal(adaptReasonsResponse({code:200}).kind, 'success');
assert.equal(adaptReasonsResponse({code:200}).options, undefined);
assert.equal(adaptReasonsResponse({code:200,data:null}).options, undefined);
assert.equal(adaptReasonsResponse({code:200,data:{id:'R1'}}).options, undefined);
assert.equal(adaptReasonsResponse({code:'200',data:[{id:'R1',name:'A'}]}).kind, 'unconfirmed');
assert.equal(adaptReasonsResponse({code:201,data:[]}).kind, 'unconfirmed');
assert.equal(adaptReasonsResponse({data:[]}).kind, 'unconfirmed');
assert.equal(adaptReasonsResponse(null).kind, 'unconfirmed');
assert.equal(adaptReasonsResponse({code:200,data:[{id:'R1',label:'旧字段'}]}).options[0].label, undefined);
assert.deepEqual(adaptReasonsResponse({code:200,data:[{id:42,name:7}]}).options, [{id:undefined,label:undefined}]);
console.log('PASS: isolated JavaScript assertions for pickImage and the private reasons adapter');
