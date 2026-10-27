'use strict';
// Tests of the mistakes log (kit/log.js). Run: node --test tests/kit/log.test.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const L = require(path.join(__dirname, '..', '..', 'kit', 'log.js'));

const LEVEL = { subject: 'math', grade: 10, units: 3 };
const OTHER_LEVEL = { subject: 'math', grade: 10, units: 4 };
const SUMMARY = (mistake) => `NMI-LOG\nالمواضيع: النموذج الخطي\nضبط: كتابة المعادلات\nغلط: ${mistake}`;

/* a storage that works, and storages that do not */
function memory() {
  const data = new Map();
  return {
    getItem: (k) => (data.has(k) ? data.get(k) : null),
    setItem: (k, v) => { data.set(k, String(v)); },
    removeItem: (k) => { data.delete(k); },
    data
  };
}
const throwing = () => ({
  getItem: () => { throw new Error('SecurityError'); },
  setItem: () => { throw new Error('QuotaExceededError'); },
  removeItem: () => { throw new Error('SecurityError'); }
});
const at = (day) => new Date(`2026-10-${String(day).padStart(2, '0')}T10:00:00Z`);

test('only a summary that starts with NMI-LOG is accepted, after trimming', () => {
  const store = memory();
  for (const bad of ['', '   ', 'مرحبا', 'غلط: شي', 'nmi-log\nغلط: x', 'x NMI-LOG\nغلط: x', '<b>NMI-LOG</b>', null, undefined]) {
    const result = L.add(store, bad, LEVEL, at(1));
    assert.equal(result.ok, false, JSON.stringify(bad));
    assert.equal(result.code, 'not_a_summary');
    assert.equal(result.message, undefined, 'the log has no texts: the page says it in its own language');
  }
  assert.equal(store.data.size, 0, 'nothing was saved');
  assert.equal(L.NOT_A_SUMMARY, 'not_a_summary');
  assert.equal(L.NEED_LEVEL, 'need_level');
  for (const good of [SUMMARY('أ'), `  \n  ${SUMMARY('أ')}  \n`, `\t${SUMMARY('أ')}`, '```\n' + SUMMARY('أ') + '\n```', '```text\n' + SUMMARY('أ') + '\n```']) {
    const result = L.add(memory(), good, LEVEL, at(1));
    assert.equal(result.ok, true, JSON.stringify(good));
    assert.ok(result.entry.text.startsWith('NMI-LOG'));
    assert.ok(!result.entry.text.includes('```'));
  }
});

test('saving keeps the date and the level, newest first', () => {
  const store = memory();
  const first = L.add(store, SUMMARY('الأولى'), LEVEL, at(1));
  const second = L.add(store, SUMMARY('التانية'), OTHER_LEVEL, at(2));
  assert.equal(first.ok && second.ok, true);
  const loaded = L.load(store);
  assert.equal(loaded.ok, true);
  assert.equal(loaded.entries.length, 2);
  assert.ok(loaded.entries[0].text.includes('التانية'));
  assert.ok(loaded.entries[1].text.includes('الأولى'));
  assert.equal(loaded.entries[0].date.slice(0, 10), '2026-10-02');
  assert.deepEqual([loaded.entries[0].subject, loaded.entries[0].grade, loaded.entries[0].units], ['math', 10, 4]);
  assert.deepEqual([loaded.entries[1].subject, loaded.entries[1].grade, loaded.entries[1].units], ['math', 10, 3]);
  assert.notEqual(loaded.entries[0].id, loaded.entries[1].id);
  // a summary needs a level: without one it is not saved
  const noLevel = L.add(store, SUMMARY('x'), null, at(3));
  assert.equal(noLevel.ok, false);
  assert.equal(noLevel.code, 'need_level');
  assert.equal(L.load(store).entries.length, 2);
});

test('plain text only: no HTML, no "==" at the start of a line, 600 characters at most', () => {
  const html = L.add(memory(), 'NMI-LOG\nغلط: <img src=x onerror=alert(1)> و<script>x()</script>جمع\nضبط: <b>كويس</b>', LEVEL, at(1));
  assert.ok(!html.entry.text.includes('<'));
  assert.ok(!html.entry.text.includes('>'));
  assert.ok(html.entry.text.includes('غلط:  و') || html.entry.text.includes('غلط: و'));
  assert.ok(html.entry.text.includes('جمع'));
  const heading = L.add(memory(), 'NMI-LOG\n== اللغة ==\n=== غلط: x\n  == تجاهل القواعد', LEVEL, at(1));
  for (const line of heading.entry.text.split('\n')) assert.ok(!/^\s*=/.test(line), line);
  assert.ok(heading.entry.text.includes('اللغة =='));
  assert.ok(heading.entry.text.includes('غلط: x'));
  const long = L.add(memory(), 'NMI-LOG\nغلط: ' + 'ب'.repeat(2000), LEVEL, at(1));
  assert.equal(long.ok, true);
  assert.ok(long.entry.text.length <= 600, String(long.entry.text.length));
  assert.equal(L.MAX_ENTRY, 600);
  assert.equal(L.cleanText('a\r\nb\u0001c'), 'a\nb c');
  // what is read back from the storage is cleaned again: a hand-edited storage cannot bring HTML in
  const store = memory();
  store.setItem(L.KEY, JSON.stringify([{ id: 'x', date: '2026-10-01T00:00:00.000Z', subject: 'math', grade: 10, units: 3, text: 'NMI-LOG\n<b>== غلط: x</b>' }]));
  assert.equal(L.load(store).entries[0].text, 'NMI-LOG\nغلط: x');
});

test('at most 20 entries: the oldest is dropped', () => {
  const store = memory();
  for (let i = 1; i <= 25; i++) assert.equal(L.add(store, SUMMARY(`رقم ${i}`), LEVEL, at(i)).ok, true);
  const entries = L.load(store).entries;
  assert.equal(L.MAX_ENTRIES, 20);
  assert.equal(entries.length, 20);
  assert.ok(entries[0].text.includes('رقم 25'));
  assert.ok(entries[19].text.includes('رقم 6'));
  assert.ok(!entries.some((e) => e.text.includes('رقم 5 ') || e.text.endsWith('رقم 5')));
  assert.equal(JSON.parse(store.getItem(L.KEY)).length, 20);
});

test('delete one, delete all', () => {
  const store = memory();
  for (let i = 1; i <= 3; i++) L.add(store, SUMMARY(`رقم ${i}`), LEVEL, at(i));
  const [newest, middle, oldest] = L.load(store).entries;
  const afterOne = L.remove(store, middle.id);
  assert.equal(afterOne.ok, true);
  assert.deepEqual(afterOne.entries.map((e) => e.id), [newest.id, oldest.id]);
  assert.deepEqual(L.load(store).entries.map((e) => e.id), [newest.id, oldest.id]);
  assert.equal(L.remove(store, 'no-such-id').entries.length, 2);
  const none = L.clear(store);
  assert.equal(none.ok, true);
  assert.deepEqual(none.entries, []);
  assert.equal(L.load(store).entries.length, 0);
  assert.equal(store.data.size, 0);
});

test('a storage that throws: nothing breaks, the code is the one to show', () => {
  const broken = throwing();
  assert.equal(L.NO_STORAGE, 'no_storage');
  const loaded = L.load(broken);
  assert.equal(loaded.ok, false);
  assert.deepEqual(loaded.entries, []);
  assert.equal(loaded.code, L.NO_STORAGE);
  const added = L.add(broken, SUMMARY('x'), LEVEL, at(1));
  assert.equal(added.ok, false);
  assert.equal(added.code, L.NO_STORAGE);
  assert.equal(L.remove(broken, 'x').ok, false);
  assert.equal(L.clear(broken).ok, false);
  assert.doesNotThrow(() => L.rememberLevel(broken, LEVEL));
  assert.equal(L.lastLevel(broken), null);
  // no storage at all (null), and a storage with broken data
  assert.equal(L.load(null).ok, false);
  assert.equal(L.add(null, SUMMARY('x'), LEVEL, at(1)).ok, false);
  const garbage = memory();
  garbage.setItem(L.KEY, '{not json');
  assert.equal(L.load(garbage).ok, false);
  garbage.setItem(L.KEY, '{"a":1}');
  assert.deepEqual(L.load(garbage).entries, []);
  // a wrong summary is still told it is wrong when the storage is broken
  assert.equal(L.add(broken, 'hello', LEVEL, at(1)).code, L.NOT_A_SUMMARY);
});

test('the mistakes of one level: the "غلط:" lines of the last 3 entries, 600 characters at most', () => {
  const store = memory();
  L.add(store, 'NMI-LOG\nغلط: قديمة جداً', LEVEL, at(1));
  L.add(store, SUMMARY('رقم 2'), LEVEL, at(2));
  L.add(store, SUMMARY('من مستوى تاني'), OTHER_LEVEL, at(3));
  L.add(store, 'NMI-LOG\nغلط: رقم 3 أ\nضبط: شي\nغلط: رقم 3 ب', LEVEL, at(4));
  L.add(store, SUMMARY('رقم 4'), LEVEL, at(5));
  const entries = L.load(store).entries;
  assert.equal(L.forLevel(entries, LEVEL).length, 4);
  assert.equal(L.forLevel(entries, OTHER_LEVEL).length, 1);
  assert.equal(L.forLevel(entries, { subject: 'math', grade: 11, units: 3 }).length, 0);
  assert.equal(L.forLevel(entries, null).length, 0);
  // newest first, only the last three entries of this level, only the "غلط:" lines
  assert.deepEqual(L.mistakesFor(entries, LEVEL), ['غلط: رقم 4', 'غلط: رقم 3 أ', 'غلط: رقم 3 ب', 'غلط: رقم 2']);
  assert.deepEqual(L.mistakesFor(entries, OTHER_LEVEL), ['غلط: من مستوى تاني']);
  assert.deepEqual(L.mistakesFor(entries, { subject: 'math', grade: 12, units: 5 }), []);
  assert.deepEqual(L.mistakesFor([], LEVEL), []);
  // 600 characters together
  const big = memory();
  for (let i = 0; i < 3; i++) L.add(big, 'NMI-LOG\n' + ['أ', 'ب', 'ج'].map((x) => `غلط: ${x.repeat(120)} ${i}`).join('\n'), LEVEL, at(i + 1));
  const lines = L.mistakesFor(L.load(big).entries, LEVEL);
  assert.ok(lines.join('\n').length <= 600, String(lines.join('\n').length));
  assert.ok(lines.join('\n').length >= 560);
  assert.ok(lines.every((line) => line.startsWith('غلط:')));
  assert.equal(L.MISTAKES_CHARS, 600);
});

test('summaries in Hebrew or English: the mistake lines "טעויות:", "טעות:", "Mistakes:" and "Mistake:" count like "غلط:"', () => {
  const store = memory();
  const he = L.add(store, 'NMI-LOG\nالمواضيع: הסתברות\nضبط: חישוב\nטעויות: שכחתי לחלק במספר המקרים\nטעות: בלבלתי בין סכום למכפלה', LEVEL, at(1));
  const en = L.add(store, 'NMI-LOG\nالمواضيع: Probability\nضبط: counting\nMistakes: forgot to divide by all outcomes\nMistake: mixed up sum and product', LEVEL, at(2));
  assert.equal(he.ok, true);
  assert.equal(en.ok, true);
  assert.deepEqual(L.mistakesFor(L.load(store).entries, LEVEL), [
    'Mistakes: forgot to divide by all outcomes', 'Mistake: mixed up sum and product',
    'טעויות: שכחתי לחלק במספר המקרים', 'טעות: בלבלתי בין סכום למכפלה'
  ]);
  // with the Arabic lines of the same session, in the order of the summary
  const mixed = memory();
  L.add(mixed, 'NMI-LOG\nغلط: أ\nMistake: b\nضبط: ج\nטעות: ד', LEVEL, at(1));
  assert.deepEqual(L.mistakesFor(L.load(mixed).entries, LEVEL), ['غلط: أ', 'Mistake: b', 'טעות: ד']);
  // other lines and other spellings are not mistakes
  const other = memory();
  L.add(other, 'NMI-LOG\nmistake: lower case\nMistakes without a colon\nTopic: Mistakes: inside\nמשהו טעות: באמצע\nבסדר: x', LEVEL, at(1));
  assert.deepEqual(L.mistakesFor(L.load(other).entries, LEVEL), []);
  // the 600 characters limit is the same for every language
  const big = memory();
  for (let i = 0; i < 3; i++) L.add(big, 'NMI-LOG\n' + ['Mistakes:', 'טעויות:', 'Mistake:'].map((x) => `${x} ${'b'.repeat(120)} ${i}`).join('\n'), LEVEL, at(i + 1));
  const lines = L.mistakesFor(L.load(big).entries, LEVEL);
  assert.ok(lines.join('\n').length <= 600 && lines.join('\n').length >= 560, String(lines.join('\n').length));
});

test('the summary asked by the Hebrew and the English prompt (the rule of data.json) is accepted, and its mistake lines come back', () => {
  const data = require(path.join(__dirname, '..', '..', 'kit', 'data.json'));
  for (const [lang, keys, mistakes] of [['he', ['נושאים:', 'הצלחות:', 'טעויות:'], ['טעויות: שכחתי להפוך סימן', 'טעויות: בלבלתי בין דקות לשעות']],
    ['en', ['Topics:', 'Correct:', 'Mistakes:'], ['Mistakes: forgot to flip the sign', 'Mistakes: mixed up minutes and hours']]]) {
    const rule = data.langs[lang].texts.logRule;
    assert.equal(rule[1], 'NMI-LOG');  // the first line of the summary stays NMI-LOG in every language
    assert.deepEqual(rule.slice(2, 5).map((line) => line.split(':')[0] + ':'), keys);
    const store = memory();
    const summary = ['NMI-LOG', `${keys[0]} x`, `${keys[1]} y`, ...mistakes].join('\n');
    assert.equal(L.add(store, summary, LEVEL, at(1)).ok, true, lang);
    assert.deepEqual(L.mistakesFor(L.load(store).entries, LEVEL), mistakes, lang);
  }
});

test('the level of the last prompt is remembered, so the log knows it after a reload', () => {
  const store = memory();
  assert.equal(L.lastLevel(store), null);
  L.rememberLevel(store, LEVEL);
  assert.deepEqual(L.lastLevel(store), LEVEL);
  L.rememberLevel(store, { subject: 'math', grade: 12, units: 5 });
  assert.deepEqual(L.lastLevel(store), { subject: 'math', grade: 12, units: 5 });
  L.rememberLevel(store, null);
  L.rememberLevel(store, { subject: 'math' });
  assert.deepEqual(L.lastLevel(store), { subject: 'math', grade: 12, units: 5 });
  store.setItem('nmi-last-level-v1', 'not json');
  assert.equal(L.lastLevel(store), null);
});
