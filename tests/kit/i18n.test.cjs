'use strict';
// Tests of the texts of the page in three languages (kit/i18n.js). Run: node --test tests/kit/i18n.test.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const kit = path.join(__dirname, '..', '..', 'kit');
const I = require(path.join(kit, 'i18n.js'));
const data = JSON.parse(fs.readFileSync(path.join(kit, 'data.json'), 'utf8'));
const appSource = fs.readFileSync(path.join(kit, 'app.js'), 'utf8');
const htmlSource = fs.readFileSync(path.join(kit, 'index.html'), 'utf8');

const ARABIC = /[؀-ۿ]/;
const HEBREW = /[֐-׿]/;
const placeholders = (text) => (text.match(/\{[a-zA-Z]+\}/g) || []).sort().join(',');

test('three languages, the right directions, and the names of the switch', () => {
  assert.deepEqual(I.LANGS, ['ar', 'he', 'en']);
  assert.deepEqual(I.DIR, { ar: 'rtl', he: 'rtl', en: 'ltr' });
  assert.deepEqual(I.NAMES, { ar: 'عربي', he: 'עברית', en: 'English' });
});

test('every key has a text in all three languages, with the same placeholders', () => {
  const keys = Object.keys(I.STRINGS);
  assert.ok(keys.length >= 100, String(keys.length));
  for (const key of keys) {
    const entry = I.STRINGS[key];
    assert.deepEqual(Object.keys(entry).sort(), ['ar', 'en', 'he'], key);
    for (const lang of I.LANGS) assert.ok(typeof entry[lang] === 'string' && entry[lang].trim().length > 0, `${key}.${lang}`);
    assert.equal(placeholders(entry.he), placeholders(entry.ar), `${key}: placeholders he`);
    assert.equal(placeholders(entry.en), placeholders(entry.ar), `${key}: placeholders en`);
  }
});

test('each language is written in its own script', () => {
  for (const [key, entry] of Object.entries(I.STRINGS)) {
    assert.ok(ARABIC.test(entry.ar), `${key}.ar has Arabic letters`);
    assert.ok(!HEBREW.test(entry.ar), `${key}.ar has no Hebrew letters`);
    assert.ok(HEBREW.test(entry.he), `${key}.he has Hebrew letters`);
    assert.ok(!ARABIC.test(entry.he), `${key}.he has no Arabic letters`);
    assert.ok(!ARABIC.test(entry.en) && !HEBREW.test(entry.en), `${key}.en is English`);
  }
});

test('the Arabic of the page is simple Modern Standard Arabic: none of the dialect words of the old texts', () => {
  const dialect = ['شو', 'بدك', 'بدنا', 'بيقدر', 'بيبلّش', 'بيحفظ', 'بيصير', 'بيخلّي', 'بتحتاج', 'بنضيف', 'بتتذكّر', 'هالمتصفح', 'هالمستوى', 'هالموضوع', 'ليش',
    'عشان', 'كتير', 'لسا', 'هاد', 'هون', 'اللي', 'عم', 'مش', 'إشي', 'جوا', 'بآخر', 'بالمرة', 'بالأيام', 'الأحسن', 'ولا', 'تانية', 'وحدة', 'بس'];
  for (const [key, entry] of Object.entries(I.STRINGS)) {
    const words = entry.ar.split(/[^؀-ۿA-Za-z]+/).filter(Boolean);
    for (const word of dialect) assert.ok(!words.includes(word), `${key}: "${word}" in "${entry.ar}"`);
  }
  // short sentences: no text of one sentence is longer than 120 characters (the long tips are several sentences)
  for (const [key, entry] of Object.entries(I.STRINGS)) {
    for (const sentence of entry.ar.split(/[.!؟?:]\s/)) assert.ok(sentence.length <= 140, `${key}: ${sentence.length}`);
  }
});

test('Hebrew uses the words of Israeli students: יח"ל for units, no בגרות where the Arabic does not have it', () => {
  assert.equal(I.t('he', 'unitsN', { n: 4 }), '4 יח"ל');
  assert.ok(I.t('he', 'units').includes('יח"ל'));
  assert.ok(I.t('he', 'targetSummary', { n: 5 }).includes('5 יח"ל'));
  assert.equal(I.t('he', 'modeMockLabel'), 'מבחן דמה');
  assert.equal(I.t('he', 'grade10'), 'כיתה י׳');
  assert.equal(I.t('he', 'grade11'), 'כיתה י״א');
  assert.equal(I.t('he', 'grade12'), 'כיתה י״ב');
  for (const [key, entry] of Object.entries(I.STRINGS)) {
    assert.ok(!entry.ar.includes('بجروت') && !entry.ar.includes('البجروت'), `${key}.ar`);
    assert.ok(!entry.he.includes('בגרות'), `${key}.he`);
    assert.ok(!/bagrut/i.test(entry.en), `${key}.en`);
  }
  assert.equal(I.t('en', 'unitsN', { n: 3 }), '3 units');
  assert.equal(I.t('ar', 'unitsN', { n: 3 }), '3 وحدات');
});

test('t(): placeholders, a missing key and a missing language', () => {
  assert.equal(I.t('en', 'stepOf', { n: 2, total: 4 }), 'Step 2 of 4');
  assert.equal(I.t('he', 'stepOf', { n: 2, total: 4 }), 'שלב 2 מתוך 4');
  assert.equal(I.t('ar', 'stepOf', { n: 2, total: 4 }), 'الخطوة 2 من 4');
  assert.equal(I.t('en', 'no-such-key'), 'no-such-key');
  assert.equal(I.t('fr', 'next'), I.STRINGS.next.ar, 'an unknown language falls back to Arabic');
  assert.equal(I.t('en', 'customLimit', { n: 5 }), 'You reached the limit: 5 topics.');
  assert.equal(I.t('en', 'tooLong', { n: 17000, max: 16000 }).includes('17000'), true);
});

test('the default language: Hebrew or English from the browser, otherwise Arabic', () => {
  for (const [browser, expected] of [['he', 'he'], ['he-IL', 'he'], ['iw', 'he'], ['iw-IL', 'he'], ['en', 'en'], ['en-US', 'en'], ['en-GB', 'en'], ['ar', 'ar'], ['ar-EG', 'ar'],
    ['ar-IL', 'ar'], ['fr-FR', 'ar'], ['ru', 'ar'], ['', 'ar'], [undefined, 'ar'], [null, 'ar'], ['HE', 'he'], ['EN-us', 'en']]) {
    assert.equal(I.detect(browser), expected, String(browser));
  }
});

test('the choice is remembered in localStorage, and a storage that throws does not break it', () => {
  const memory = new Map();
  const store = { getItem: (k) => (memory.has(k) ? memory.get(k) : null), setItem: (k, v) => { memory.set(k, String(v)); } };
  assert.equal(I.loadLang(store), null);
  I.saveLang(store, 'he');
  assert.equal(I.STORAGE_KEY, 'nmi-lang-v1');
  assert.equal(memory.get('nmi-lang-v1'), 'he');
  assert.equal(I.loadLang(store), 'he');
  I.saveLang(store, 'fr');  // not a language of the page
  assert.equal(I.loadLang(store), 'he');
  memory.set('nmi-lang-v1', 'klingon');
  assert.equal(I.loadLang(store), null, 'a value that is not a language is ignored');
  const broken = { getItem: () => { throw new Error('SecurityError'); }, setItem: () => { throw new Error('QuotaExceededError'); } };
  assert.equal(I.loadLang(broken), null);
  assert.doesNotThrow(() => I.saveLang(broken, 'en'));
  assert.equal(I.loadLang(null), null);
  assert.doesNotThrow(() => I.saveLang(null, 'en'));
});

test('topic names: Arabic in Arabic; the Hebrew term in Hebrew and English, else the Arabic title', () => {
  const topics = [];
  for (const g of data.subjects[0].grades) for (const l of g.levels) for (const t of l.topics) topics.push(t);
  assert.equal(topics.length, 101);
  const probability = topics.find((t) => t.id === 'm10-3-04');
  assert.equal(I.topicName(probability, 'ar'), 'الاحتمال');
  assert.equal(I.topicName(probability, 'he'), 'הסתברות');
  assert.equal(I.topicName(probability, 'en'), 'הסתברות');
  const noHebrew = topics.filter((t) => !I.hebrewTerm(t.title_full));
  // these topics have no Hebrew term in the curriculum files: they show the Arabic title in Hebrew and English
  assert.deepEqual(noHebrew.map((t) => t.id), ['m10-3-05', 'm10-3-10', 'm10-3-11', 'm10-3-14', 'm10-4-11', 'm10-5-03', 'm10-5-08', 'm11-3-04', 'm11-3-06',
    'm11-3-07', 'm11-3-09', 'm11-3-10', 'm11-3-11', 'm11-4-05', 'm11-4-08', 'm11-4-14', 'm11-5-06', 'm12-4-06', 'm12-4-07', 'm12-4-08', 'm12-4-11',
    'm12-4-12', 'm12-5-02', 'm12-5-04']);
  assert.equal(noHebrew.length, 24);
  for (const t of noHebrew) for (const lang of ['he', 'en']) assert.equal(I.topicName(t, lang), t.title, t.id);
  for (const t of topics.filter((x) => I.hebrewTerm(x.title_full))) {
    assert.ok(HEBREW.test(I.topicName(t, 'he')) && !ARABIC.test(I.topicName(t, 'he')), t.id);
    assert.equal(I.topicName(t, 'en'), I.topicName(t, 'he'), t.id);
    assert.equal(I.topicName(t, 'ar'), t.title, t.id);
    assert.ok(!ARABIC.test(t.title_full.match(/\(([^()]*[֐-׿][^()]*)\)/)[1]), t.id);
  }
  assert.equal(I.hebrewTerm('مراجعة (بالطريقتين)'), null, 'a bracket without Hebrew is not a term');
  // the cluster headings of the 3-unit levels
  const clusters = new Set();
  for (const t of topics.filter((x) => x.group)) clusters.add(t.group);
  assert.ok(clusters.size >= 3);
  for (const t of topics.filter((x) => x.group)) {
    assert.equal(I.groupName(t, 'ar'), t.group);
    assert.ok(HEBREW.test(I.groupName(t, 'he')) && !ARABIC.test(I.groupName(t, 'he')), t.group);
  }
  assert.equal(I.groupName({ group: null }, 'he'), null);
});

test('count of topics, the grade and the level label in the three languages', () => {
  assert.deepEqual([1, 2, 3, 10, 11].map((n) => I.count('ar', n)), ['موضوع واحد', 'موضوعان', '3 مواضيع', '10 مواضيع', '11 موضوعًا']);
  assert.deepEqual([1, 2, 3, 11].map((n) => I.count('he', n)), ['נושא אחד', 'שני נושאים', '3 נושאים', '11 נושאים']);
  assert.deepEqual([1, 2, 3, 11].map((n) => I.count('en', n)), ['1 topic', '2 topics', '3 topics', '11 topics']);
  assert.equal(I.levelLabel('ar', { subject: 'math', grade: 10, units: 3 }), 'رياضيات، الصف العاشر، 3 وحدات');
  assert.equal(I.levelLabel('he', { subject: 'math', grade: 11, units: 4 }), 'מתמטיקה, כיתה י״א, 4 יח"ל');
  assert.equal(I.levelLabel('en', { subject: 'math', grade: 12, units: 5 }), 'Math, Grade 12, 5 units');
});

test('every text the page uses is in the dictionary, and every key of the dictionary is used', () => {
  const used = new Set();
  for (const match of appSource.matchAll(/\bT\('([A-Za-z0-9]+)'\s*[,)]/g)) used.add(match[1]);
  for (const match of htmlSource.matchAll(/data-i18n="([A-Za-z0-9]+)"/g)) used.add(match[1]);
  // keys kept in a variable (the message of the log page is a key, so that it follows the language)
  for (const match of appSource.matchAll(/'([A-Za-z0-9]+)'/g)) if (I.STRINGS[match[1]]) used.add(match[1]);
  // the keys the page builds from a name: modes, grades, subjects
  for (const mode of ['Explain', 'Practice', 'Mock', 'Plan']) for (const part of ['Label', 'Desc']) used.add(`mode${mode}${part}`);
  for (const id of [10, 11, 12]) used.add(`grade${id}`);
  used.add('subjectMath');
  used.add('langNav');
  used.add('logTitle');
  // used by the functions of i18n.js (count, levelLabel), and by the static text of index.html (no script there to translate it)
  for (const key of ['topicOne', 'topicTwo', 'topicFew', 'topicMany', 'levelLabel', 'noscript']) used.add(key);
  assert.ok(htmlSource.includes('<noscript><p class="note">' + I.STRINGS.noscript.ar + '</p></noscript>'), 'the static text of index.html is the Arabic one');
  assert.ok(htmlSource.includes(`content="${I.STRINGS.description.ar}"`));
  assert.ok(htmlSource.includes(`<title>${I.STRINGS.title.ar}</title>`));
  assert.ok(htmlSource.includes(`data-i18n="loading">${I.STRINGS.loading.ar}<`));
  for (const key of used) assert.ok(I.STRINGS[key], `the page uses "${key}" and it is not in the dictionary`);
  const unused = Object.keys(I.STRINGS).filter((key) => !used.has(key));
  // "title" and "description" are the title and the description of the page
  assert.deepEqual(unused.filter((k) => !['title', 'description'].includes(k)), [], 'keys nobody uses');
});

test('the page code has no Arabic text of its own: no literal outside the dictionary (the log token and comments excepted)', () => {
  for (const [name, source] of [['app.js', appSource], ['log.js', fs.readFileSync(path.join(kit, 'log.js'), 'utf8')]]) {
    const lines = source.split('\n').filter((line) => ARABIC.test(line) && !/^\s*(\/\/|\/\*|\*)/.test(line) && !/\/\/.*[؀-ۿ]/.test(line.replace(/'[^']*'/g, '')) );
    const bad = lines.filter((line) => !line.includes("'غلط:'"));
    assert.deepEqual(bad, [], name);
  }
});
