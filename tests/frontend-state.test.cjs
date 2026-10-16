const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('preview/preview.js', 'utf8');
const { COPY, parseDemo, SUPPORTED_GRADES } = vm.runInNewContext(source.slice(0, source.indexOf('const $')) + '; ({COPY,parseDemo,SUPPORTED_GRADES});');
const base = {version:1,profile:{name:'Demo',country:'Jordan',grade:10,language:'en',avatar:false,subjects:['math']},chats:[]};
const { COUNTRIES, academicPolicy } = vm.runInNewContext(source.slice(0, source.indexOf('const $')) + '; ({COUNTRIES,academicPolicy});');
test('exactly ten approved countries; coded profiles require matching supported country', () => {
  assert.equal(JSON.stringify(COUNTRIES.map(c => c.code)), '["US","GB","CA","DE","CH","SG","AU","NL","QA","AE"]');
  for (const country of COUNTRIES) assert.equal(parseDemo(JSON.stringify({...base,profile:{...base.profile,country:country.en,countryCode:country.code}})).profile.countryCode,country.code);
  for (const countryCode of ['FR','JO','',null,'USA']) assert.throws(() => parseDemo(JSON.stringify({...base,profile:{...base.profile,countryCode}})));
  assert.throws(() => parseDemo(JSON.stringify({...base,profile:{...base.profile,countryCode:'US'}})));
});
test('any topic may chat; academic capabilities allow exactly three subjects', () => {
  for (const subject of ['math','physics','chemistry','code','writing','science','history','biology','general',null]) {
    const policy = academicPolicy(subject); const eligible = ['math','physics','chemistry'].includes(subject);
    assert.equal(policy.chatAllowed,true); assert.equal(policy.preserveConversation,true);
    for (const key of ['curriculumEligible','assessmentEligible','masteryEligible','progressEligible']) assert.equal(policy[key],eligible);
  }
});
test('legacy country and non-academic interests remain intact', () => {
  const profile = {...base.profile,subjects:['science','code','writing']};
  const restored = parseDemo(JSON.stringify({...base,profile}));
  assert.equal(restored.profile.country,'Jordan'); assert.equal(JSON.stringify(restored.profile.subjects),JSON.stringify(profile.subjects));
  assert.equal(restored.profile.countryCode,undefined);
});
test('two complete dictionaries; every HTML translation is defined', () => {
  assert.deepEqual(Object.keys(COPY.ar).sort(), Object.keys(COPY.en).sort());
  for (const [key,text] of Object.entries(COPY.ar)) { assert.match(text, /[\u0600-\u06ff]|NMI/); assert.doesNotMatch(text,/\?{2,}|undefined/); }
  for (const match of fs.readFileSync('preview/index.html','utf8').matchAll(/data-(?:i18n|label|placeholder)="([^"]+)"/g)) assert.ok(COPY.ar[match[1]],match[1]);
});
test('only grades 9 through 12; future/invalid enrollment rejected', () => {
  assert.equal(JSON.stringify(SUPPORTED_GRADES),'[9,10,11,12]');
  for (const grade of [9,10,11,12]) assert.equal(parseDemo(JSON.stringify({...base,profile:{...base.profile,grade}})).profile.grade,grade);
  for (const grade of [1,8,13,0,'10',null,10.5]) assert.throws(() => parseDemo(JSON.stringify({...base,profile:{...base.profile,grade}})));
});
test('malformed, wrong-version, oversized and wrong-shaped storage rejected', () => {
  assert.equal(parseDemo(null),null);
  for (const raw of ['{bad','null','[]','"text"','x'.repeat(1000001),JSON.stringify({...base,version:2}),JSON.stringify({...base,chats:{}})]) assert.throws(() => parseDemo(raw));
  for (const patch of [{name:''},{name:'x'.repeat(41)},{country:''},{language:'fr'},{avatar:1},{subjects:['math','math']},{subjects:['unknown']}]) assert.throws(() => parseDemo(JSON.stringify({...base,profile:{...base.profile,...patch}})));
});
test('safe reconstruction excludes unknown data and preserves text literally', () => {
  const chats=[{id:'local-1',title:'Sample',kind:'math',messages:[{role:'user',text:'<img src=x onerror=alert(1)>'},{role:'assistant',kind:'math'},{role:'assistant',kind:'hint',topic:'math'},{role:'notice',key:'stopped'}]}];
  const result=parseDemo(JSON.stringify({...base,extra:'discard',profile:{...base.profile,token:'discard'},chats}));
  assert.equal(result.extra,undefined); assert.equal(result.profile.token,undefined); assert.equal(result.chats[0].messages[0].text,chats[0].messages[0].text);
  for (const message of [{role:'assistant',kind:'unknown'},{role:'assistant',kind:'hint',topic:'unknown'},{role:'user',key:'arbitrary'},{role:'notice',key:'unknown'},{role:'user',text:'x'.repeat(4001)}]) assert.throws(() => parseDemo(JSON.stringify({...base,chats:[{...chats[0],messages:[message]}]})));
  assert.throws(() => parseDemo(JSON.stringify({...base,chats:[chats[0],chats[0]]})));
});
