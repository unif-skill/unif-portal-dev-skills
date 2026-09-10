// 合成代码评测：导入被测产物，只替换外部边界；不调用业务工程或真实服务。
import assert from 'node:assert/strict';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const outputRoot=path.resolve(process.argv[2]);
const variant=process.argv[3];
const results=[];
const modules={};
for (const name of ['design','adapter','internal']) {
  modules[name]=await import(pathToFileURL(path.join(outputRoot,`${variant}-${name}`,'solution.mjs')));
}
function boundary(allowed) {
  return new Proxy(allowed,{get(target,key) {
    if (key in target) return target[key];
    throw new Error(`unexpected dependency: ${String(key)}`);
  }});
}
async function check(name,run) {
  const calls=[];
  try { await run(calls); results.push({name,passed:true,calls}); }
  catch (error) { results.push({name,passed:false,error:error.message,calls}); }
}
const location={latitude:31,longitude:121};
const query={customerId:'C-NEW',location,page:1};
const page={kind:'success',items:[{id:'item-1'}],nextPage:2};

await check('I1 explicit refresh reacquires location before query',async calls=>{
  const actual=await modules.design.refreshNearby({customerId:'C-NEW',previousLocation:{latitude:0,longitude:0}},boundary({
    location:{async read(){calls.push(['location']);return location;}},
    transport:{async query(input){calls.push(['query',input]);return page;}},
  }));
  assert.deepEqual(calls,[['location'],['query',query]]);
  assert.deepEqual(actual.location,location);
  assert.deepEqual(actual.result,page);
});
await check('I2 missing or invalid query input has no external call',async calls=>{
  for (const input of [{},{customerId:'C-NEW',page:1},{location,page:1},{customerId:'C-NEW',location},{...query,page:0}]) {
    const result=await modules.design.queryNearby(input,boundary({transport:{async query(value){calls.push(['query',value]);throw Error('must not query');}}}));
    assert.equal(result.kind,'invalid-input');
  }
  assert.deepEqual(calls,[]);
});
await check('I2-I3 explicit inputs one page no ambient dependency',async calls=>{
  const actual=await modules.design.queryNearby(query,boundary({transport:{async query(input){calls.push(['query',input]);return page;}}}));
  assert.deepEqual(calls,[['query',query]]);
  assert.deepEqual(actual,page);
});
await check('I3 explicit next-page call preserves supplied customer and location',async calls=>{
  const next={...query,page:2};
  const last={kind:'success',items:[]};
  const actual=await modules.design.queryNearby(next,boundary({transport:{async query(input){calls.push(['query',input]);return last;}}}));
  assert.deepEqual(calls,[['query',next]]);
  assert.deepEqual(actual,last);
});
await check('I4 query transport exception remains unchanged',async calls=>{
  const failure=new Error('synthetic transport');
  await assert.rejects(modules.design.queryNearby(query,boundary({transport:{async query(input){calls.push(['query',input]);throw failure;}}})),error=>error===failure);
  assert.equal(calls.length,1);
});

const reasonInput={customerId:'C-NEW',page:3};
function reasonDeps(raw,calls) {
  return boundary({api:boundary({async list(input){calls.push(['list',input]);return raw;}})});
}
await check('B1 missing reason input has no ambient fallback or request',async calls=>{
  for (const input of [{},{page:3},{customerId:'C-NEW'},{...reasonInput,page:0}]) {
    const actual=await modules.adapter.readReasons(input,reasonDeps({code:200,data:[]},calls));
    assert.equal(actual.kind,'invalid-input');
  }
  assert.deepEqual(calls,[]);
});
await check('B1-B2 one list call maps rows without detail cache or autopaging',async calls=>{
  const raw={code:200,data:[{id:'R1'},null,{id:'R2',name:'名称'},{id:'R2',name:'重复'},{id:'R3',label:'旧字段'}],nextPage:4};
  const actual=await modules.adapter.readReasons(reasonInput,reasonDeps(raw,calls));
  assert.deepEqual(calls,[['list',reasonInput]]);
  assert.equal(actual.kind,'success');
  assert.equal(actual.nextPage,4);
  assert.equal(actual.options.length,5);
  assert.deepEqual(actual.options.map(item=>[item?.id,item?.label]),[
    ['R1',undefined],[undefined,undefined],['R2','名称'],['R2','重复'],['R3',undefined],
  ]);
});
await check('B2 empty page and absent display data remain distinct successes',async calls=>{
  const empty=await modules.adapter.readReasons(reasonInput,reasonDeps({code:200,data:[]},calls));
  const absent=await modules.adapter.readReasons(reasonInput,reasonDeps({code:200},calls));
  assert.equal(empty.kind,'success');assert.deepEqual(empty.options,[]);
  assert.equal(absent.kind,'success');assert.equal(absent.options,undefined);
  assert.equal(calls.length,2);
});
await check('B2 unknown or string business code does not confirm success',async calls=>{
  for (const raw of [{code:'200',data:[]},{code:503},{data:[]}]) {
    assert.equal((await modules.adapter.readReasons(reasonInput,reasonDeps(raw,calls))).kind,'unconfirmed');
  }
  assert.equal(calls.length,3);
});
await check('B3 actual readReasons propagates API failure',async calls=>{
  const failure=new Error('synthetic reason API');
  await assert.rejects(modules.adapter.readReasons(reasonInput,boundary({api:{async list(input){calls.push(['list',input]);throw failure;}}})),error=>error===failure);
  assert.deepEqual(calls,[['list',reasonInput]]);
});

const customer={customerId:'C-NEW'};
await check('N1 existing draft is reused within the confirmed public operation',async calls=>{
  const draft={id:'D1',...customer};
  const actual=await modules.internal.ensureDraft(customer,boundary({api:boundary({async find(input){calls.push(['find',input]);return draft;}})}));
  assert.deepEqual(actual,draft);assert.deepEqual(calls,[['find',customer]]);
});
await check('N1 missing draft is created inside ensureDraft after find',async calls=>{
  const draft={id:'D2',...customer};
  const actual=await modules.internal.ensureDraft(customer,boundary({api:{
    async find(input){calls.push(['find',input]);return null;},
    async create(input){calls.push(['create',input]);return draft;},
  }}));
  assert.deepEqual(actual,draft);assert.deepEqual(calls,[['find',customer],['create',customer]]);
});
await check('N1 failed lookup does not trigger create or retry',async calls=>{
  const failure=new Error('synthetic lookup');
  await assert.rejects(modules.internal.ensureDraft(customer,boundary({api:boundary({async find(input){calls.push(['find',input]);throw failure;}})})),error=>error===failure);
  assert.deepEqual(calls,[['find',customer]]);
});
function cameraDeps(calls,{cancel=false,adoptFailure,captureFailure}={}) {
  return boundary({device:{async open(input){calls.push(['open',input]);return {
    async capture(){calls.push(['capture']);if(captureFailure) throw captureFailure;return cancel?{kind:'cancelled'}:{kind:'selected',temporaryPath:'/synthetic/temp-photo'};},
    async close(){calls.push(['close']);},
  };}},files:{
    async adopt(value){calls.push(['adopt',value]);if(adoptFailure)throw adoptFailure;return {uri:'local:persisted'};},
    async remove(value){calls.push(['remove',value]);},
  }});
}
await check('N2 selected photo adopted and temporary resource plus session released',async calls=>{
  const actual=await modules.internal.capturePhoto({lens:'rear'},cameraDeps(calls));
  assert.deepEqual(actual,{kind:'success',uri:'local:persisted'});
  assert.deepEqual(calls.filter(c=>c[0]!=='close'),[
    ['open',{lens:'rear'}],['capture'],['adopt','/synthetic/temp-photo'],['remove','/synthetic/temp-photo'],
  ]);
  assert.equal(calls.filter(c=>c[0]==='close').length,1);
  assert.ok(calls.findIndex(c=>c[0]==='close')>calls.findIndex(c=>c[0]==='capture'));
});
await check('N2 cancellation releases session without file operations',async calls=>{
  assert.deepEqual(await modules.internal.capturePhoto({},cameraDeps(calls,{cancel:true})),{kind:'cancelled'});
  assert.deepEqual(calls,[['open',{}],['capture'],['close']]);
});
await check('N2 adopt failure cleans the selected temporary file and closes session',async calls=>{
  const failure=new Error('synthetic adopt');
  await assert.rejects(modules.internal.capturePhoto({},cameraDeps(calls,{adoptFailure:failure})),error=>error===failure);
  assert.equal(calls.filter(c=>c[0]==='adopt').length,1);
  assert.deepEqual(calls.filter(c=>c[0]==='remove'),[['remove','/synthetic/temp-photo']]);
  assert.equal(calls.filter(c=>c[0]==='close').length,1);
});
await check('N2 capture failure closes session without inventing a temporary path',async calls=>{
  const failure=new Error('synthetic capture');
  await assert.rejects(modules.internal.capturePhoto({},cameraDeps(calls,{captureFailure:failure})),error=>error===failure);
  assert.deepEqual(calls,[['open',{}],['capture'],['close']]);
});
console.log(JSON.stringify({variant,checks:results.length,passed:results.filter(r=>r.passed).length,results},null,2));
process.exitCode=results.some(r=>!r.passed)?1:0;
