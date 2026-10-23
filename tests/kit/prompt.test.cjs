'use strict';
// Tests of the prompt the kit builds (kit/prompt.js + kit/data.json). Run: node --test tests/kit
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const kit = path.join(__dirname, '..', '..', 'kit');
const data = JSON.parse(fs.readFileSync(path.join(kit, 'data.json'), 'utf8'));
const P = require(path.join(kit, 'prompt.js'));
const ID = /m\d+-\d+-\d+/;

const math = data.subjects.find((s) => s.id === 'math');
const level = (grade, units) => P.findLevel(data, 'math', grade, units).level;
const build = (extra) => P.buildPrompt(data, Object.assign({ subject: 'math', grade: 10, units: 3, target: null, all: false, topics: [], mode: 'bagrut' }, extra));
const firstLine = (topic) => topic.text.split('\n')[0];

test('the data covers every level, and only grade 10 has the example bank', () => {
  assert.equal(math.grades.length, 3);
  const flags = {};
  for (const g of math.grades) for (const l of g.levels) flags[`${g.id}/${l.units}`] = l.experimental;
  assert.deepEqual(flags, { '10/3': false, '10/4': false, '10/5': false, '11/3': true, '11/4': true, '11/5': true, '12/3': true, '12/4': true, '12/5': true });
});

test('the prompt holds only the chosen topics, with their text and no other topic', () => {
  const l = level(10, 4);
  const chosen = ['m10-4-06', 'm10-4-10'];
  const { text, topics } = build({ units: 4, topics: chosen });
  assert.equal(topics, 2);
  for (const topic of l.topics) {
    const heading = `### ${topic.title_full}`;
    if (chosen.includes(topic.id)) {
      assert.ok(text.includes(heading), topic.id);
      assert.ok(text.includes(firstLine(topic)), topic.id);
    } else {
      assert.ok(!text.includes(heading), topic.id);
      if (firstLine(topic)) assert.ok(!text.includes(firstLine(topic)), topic.id);
    }
  }
  assert.match(text, /المواضيع اللي بدو يراجعها: التفاضل، الاحتمال\n/);
  // topics of another level never leak in
  assert.ok(!text.includes(level(10, 5).topics[0].title_full));
  assert.ok(!text.includes(level(11, 4).topics.find((t) => t.id === 'm11-4-06').title_full));
});

test('"all topics" lists every topic of the level', () => {
  const l = level(10, 3);
  const { text } = build({ all: true });
  assert.match(text, /المواضيع اللي بدو يراجعها: كل المواضيع\n/);
  for (const topic of l.topics) assert.ok(text.includes(`### ${topic.title_full}`), topic.id);
});

test('the Bagrut patterns are the ones of the level (and the grade, for a form written for one grade)', () => {
  const t4 = build({ units: 4, topics: ['m10-4-06'] }).text;
  assert.ok(t4.includes('35471') && t4.includes('35472'));
  assert.ok(!t4.includes('35172') && !t4.includes('35571') && !t4.includes('35572'));
  const t5 = build({ units: 5, topics: ['m10-5-06'] }).text;
  assert.ok(t5.includes('35571') && t5.includes('35572'));
  assert.ok(!t5.includes('35471'));
  const g10 = build({ topics: ['m10-3-12'] }).text;
  assert.ok(g10.includes('35172') && g10.includes('35371'));
  assert.ok(!g10.includes('الصف الثاني عشر: استمارة 35372'), 'the 12th-grade form is not for a 10th grader');
  const g12 = P.buildPrompt(data, { subject: 'math', grade: 12, units: 3, target: null, all: false, topics: ['m12-3-02'], mode: 'bagrut' }).text;
  assert.ok(g12.includes('الصف الثاني عشر: استمارة 35372'));
  assert.ok(!g12.includes('استمارة 35172'), 'the 10th-grade form is not for a 12th grader');
  // the general rules and "how the tutor writes a question" are always there
  for (const text of [t4, t5, g10, g12]) {
    assert.ok(text.includes('## قواعد عامة لكل سؤال بجروت'));
    assert.ok(text.includes('## كيف المدرّس يكتب سؤال تدريب بنمط البجروت'));
  }
});

test('the example is the one of the chosen topic, with the "do not return it" sentence', () => {
  const l = level(10, 3);
  const linear = l.topics.find((t) => t.id === 'm10-3-12');
  const { text } = build({ topics: ['m10-3-12'] });
  assert.ok(text.includes('-- مثال على الشكل، ما تعيده'));
  assert.ok(text.includes(linear.example));
  for (const topic of l.topics) if (topic.id !== 'm10-3-12') assert.ok(!text.includes(topic.example), topic.id);
  // several chosen topics: the first one in the curriculum order that has an example
  const several = build({ topics: ['m10-3-13', 'm10-3-03'] }).text;
  assert.ok(several.includes(l.topics.find((t) => t.id === 'm10-3-03').example));
  assert.ok(!several.includes(l.topics.find((t) => t.id === 'm10-3-13').example));
  // a level without the bank is flagged, not filled with an invented example
  const experimental = P.buildPrompt(data, { subject: 'math', grade: 11, units: 4, target: null, all: false, topics: ['m11-4-01'], mode: 'bagrut' });
  assert.ok(!experimental.text.includes('ما تعيده'));
  assert.equal(experimental.missingExample, true);
  assert.equal(build({ topics: ['m10-3-12'] }).missingExample, false);
});

test('no "ملف" and no topic ids, except the ids in plan mode', () => {
  const cases = [];
  for (const g of math.grades) for (const l of g.levels) for (const mode of ['explain', 'bagrut', 'plan']) cases.push([g.id, l.units, mode]);
  assert.equal(cases.length, 27);
  for (const [grade, units, mode] of cases) {
    const l = level(grade, units);
    const { text } = P.buildPrompt(data, { subject: 'math', grade, units, target: null, all: true, topics: [], mode });
    const label = `${grade}/${units}/${mode}`;
    assert.ok(!text.includes('ملف'), label);
    assert.ok(!text.includes('- مرفق:'), label);
    assert.ok(text.includes('- تحت:'), label + ' (the content is inside the prompt: "تحت")');
    if (mode === 'plan') {
      for (const topic of l.topics) assert.ok(text.includes(`### ${topic.id} `), label + ' ' + topic.id);
      assert.ok(text.includes('## أرقام الاستمارات'), label);
    } else {
      assert.ok(!ID.test(text), label + ' ' + (text.match(ID) || [''])[0]);
      assert.ok(!text.includes('## أرقام الاستمارات'), label);
    }
  }
  // a topic that points to another topic by its number (grade 10, 4 units) loses the number outside plan mode
  assert.ok(level(10, 4).topics[0].text.includes('(m10-4-05)'));
  const analytic = build({ units: 4, topics: ['m10-4-01'] }).text;
  assert.ok(analytic.includes('بييجي بعدين.') && !analytic.includes('m10-4-05'));
  assert.ok(P.buildPrompt(data, { subject: 'math', grade: 10, units: 4, target: null, all: false, topics: ['m10-4-01'], mode: 'plan' }).text.includes('(m10-4-05)'));
});

test('the base prompt sections are filled; "مرفق" became "تحت"; no dialect rule is added', () => {
  const { text } = build({ topics: ['m10-3-12'] });
  for (const part of ['المادة: رياضيات', 'الصف: العاشر', 'الوحدات: 3', 'الهدف: ما في هدف خاص', 'الوضع اللي اختاره: تدرّب بجروت',
    '- تحت: منهاج صف ووحدات الطالب', '== سلّم التلميحات (بالتمرين والتدرّب) ==', '== صور الحلول ==', '== قواعد لكل رد ==',
    'جاوب بنفس لغة الطالب']) assert.ok(text.includes(part), part);
  assert.ok(!text.includes('['), 'no placeholder left');
  assert.ok(!text.includes('لهجة'));
  assert.ok(!text.includes('فلسطين'));
  // the sections keep the order of the base prompt
  const order = ['== الطالب ==', '== المصادر ==', '== اللغة ==', '== الأوضاع ==', '== سلّم التلميحات', '== صور الحلول ==', '== قواعد لكل رد =='];
  const positions = order.map((o) => text.indexOf(o));
  assert.deepEqual([...positions].sort((a, b) => a - b), positions);
  assert.ok(positions.every((p) => p >= 0));
});

test('each mode ends with its own first move', () => {
  const ends = {};
  for (const mode of ['explain', 'bagrut', 'plan']) ends[mode] = build({ all: true, mode }).text.trim().split('\n').pop();
  assert.match(ends.explain, /أي موضوع بدك أشرحلك/);
  assert.match(ends.bagrut, /سؤال بجروت جديد/);
  assert.match(ends.plan, /كم أسبوع باقي للامتحان/);
  assert.ok(!Object.values(ends).some((l) => l.includes('شو بدك اليوم')));
});

test('a target level adds its topics, its patterns and the goal line', () => {
  const { text } = build({ target: 5, all: true });
  assert.ok(text.includes('الهدف: الانتقال من 3 لـ 5 وحدات'));
  assert.ok(text.includes('-- منهاج الطالب (مستوى الهدف)'));
  for (const topic of level(10, 5).topics) assert.ok(text.includes(`### ${topic.title_full}`), topic.id);
  assert.ok(text.includes('35571'));
  // a target that is not higher is ignored
  const same = build({ units: 4, target: 3, all: true }).text;
  assert.ok(same.includes('الهدف: ما في هدف خاص'));
  assert.ok(!same.includes('(مستوى الهدف)'));
});

test('the length limit: one whole level fits, a very big choice is flagged', () => {
  assert.equal(P.MAX_LENGTH, 14000);
  for (const g of math.grades) for (const l of g.levels) {
    for (const mode of ['explain', 'bagrut', 'plan']) {
      const built = P.buildPrompt(data, { subject: 'math', grade: g.id, units: l.units, target: null, all: true, topics: [], mode });
      assert.equal(built.length, built.text.length);
      assert.ok(built.length <= P.MAX_LENGTH, `${g.id}/${l.units}/${mode}: ${built.length}`);
      assert.equal(built.tooLong, false);
    }
  }
  const big = build({ target: 5, all: true });
  assert.ok(big.length > P.MAX_LENGTH);
  assert.equal(big.tooLong, true);
});

test('an unknown level gives no prompt', () => {
  assert.equal(P.buildPrompt(data, { subject: 'math', grade: 9, units: 3, all: true, topics: [], mode: 'explain' }), null);
  assert.equal(P.buildPrompt(data, { subject: 'chemistry', grade: 10, units: 3, all: true, topics: [], mode: 'explain' }), null);
});
