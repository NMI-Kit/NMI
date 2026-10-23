/* Builds the prompt the student pastes into ChatGPT, Claude or Gemini.
   Pure functions: no DOM, no network. Used by app.js in the page and by the node tests. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NMIPrompt = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* Longest prompt we are happy to send, in characters. A whole 5-unit level is about 12,000, so one level with
     every topic fits. About 14,000 characters is a bit under 5,000 tokens in Arabic: a free-tier chat takes it, a
     phone pastes it without trouble, and the model still follows the rules at the top instead of drowning in text. */
  const MAX_LENGTH = 14000;

  const MODES = {
    explain: { label: 'شرح', chosen: 'شرح', start: 'ابدأ بسؤال الطالب: "أي موضوع بدك أشرحلك؟"' },
    bagrut: { label: 'تدرّب بجروت', chosen: 'تدرّب بجروت', start: 'ابدأ مباشرة بسؤال بجروت جديد على موضوع من اللي اختارهم الطالب: القصة والقسم أ بس، واستنى حله.' },
    plan: { label: 'خطة', chosen: 'خطة', start: 'ابدأ بسؤال الطالب: "كم أسبوع باقي للامتحان، وكم ساعة بتقدر تدرس بالأسبوع؟" وبعدين اعمل الخطة.' }
  };

  const ID = /m\d+-\d+-\d+/;
  const ID_IN_PARENS = /\s*\(m\d+-\d+-\d+\)/g;
  const BARE_ID = /m\d+-\d+-\d+/g;

  function findSubject(data, subjectId) {
    return data.subjects.find(function (s) { return s.id === subjectId; }) || null;
  }

  function findLevel(data, subjectId, gradeId, units) {
    const subject = findSubject(data, subjectId);
    const grade = subject && subject.grades.find(function (g) { return g.id === Number(gradeId); });
    const level = grade && grade.levels.find(function (l) { return l.units === Number(units); });
    return level ? { subject: subject, grade: grade, level: level } : null;
  }

  function withoutIds(text) {
    return text.replace(ID_IN_PARENS, '').replace(BARE_ID, 'موضوع تاني');
  }

  /* Level sections of the Bagrut patterns for the student's level (and the target level), plus the general rules and the
     "how the tutor writes a question" part. The table of form numbers is only for the plan mode. */
  function patternsText(subject, gradeName, unitsList, mode) {
    const p = subject.patterns;
    if (!p) return '';
    const parts = [];
    if (mode === 'plan' && p.forms) parts.push(p.forms);
    if (p.general) parts.push(p.general);
    unitsList.forEach(function (units) {
      (p.levels[String(units)] || []).forEach(function (section) {
        /* a form written for one grade (for example the 12th-grade form) is only for that grade */
        if (!section.grade || section.grade === gradeName) parts.push(section.text);
      });
    });
    if (p.howto) parts.push(p.howto);
    return parts.filter(Boolean).join('\n\n');
  }

  function topicBlock(topic, mode) {
    const heading = mode === 'plan' ? '### ' + topic.id + ' ' + topic.title_full : '### ' + topic.title_full;
    const body = mode === 'plan' ? topic.text : withoutIds(topic.text);
    return body ? heading + '\n' + body : heading;
  }

  function splitSections(base) {
    /* "== اسم ==" lines start a section; returns [{name, lines}] and the text before the first one. */
    const out = [];
    let head = [];
    let current = null;
    base.split('\n').forEach(function (line) {
      const m = line.match(/^== (.+) ==\s*$/);
      if (m) {
        current = { name: m[1], lines: [] };
        out.push(current);
      } else if (current) current.lines.push(line);
      else head.push(line);
    });
    return { head: head, sections: out };
  }

  function listOfTitles(topics) {
    return topics.map(function (t) { return t.title; }).join('، ');
  }

  /* sel: { subject, grade, units, target (units or null), topics (ids, from the level or the target level), all (bool), mode }
     Returns { text, length, tooLong, max, missing } or null when the level does not exist. */
  function buildPrompt(data, sel) {
    const mode = MODES[sel.mode] ? sel.mode : 'explain';
    const found = findLevel(data, sel.subject, sel.grade, sel.units);
    if (!found) return null;
    const subject = found.subject;
    const levels = [found.level];
    const target = sel.target && Number(sel.target) > Number(sel.units) ? findLevel(data, sel.subject, sel.grade, sel.target) : null;
    if (target) levels.push(target.level);

    const chosenIds = new Set(sel.topics || []);
    const pool = [];
    levels.forEach(function (level) { level.topics.forEach(function (t) { pool.push({ topic: t, level: level }); }); });
    const picked = sel.all ? pool : pool.filter(function (entry) { return chosenIds.has(entry.topic.id); });

    const { head, sections } = splitSections(data.base_prompt);
    const section = function (name) { return sections.find(function (s) { return s.name === name; }); };
    let title = head.join('\n').trim();
    if (subject.name && subject.id !== 'math') title = title.replace('رياضيات', subject.name);

    /* == الطالب == */
    const student = [];
    student.push('المادة: ' + subject.name);
    student.push('الصف: ' + found.grade.name);
    student.push('الوحدات: ' + sel.units);
    student.push(target ? 'الهدف: الانتقال من ' + sel.units + ' لـ ' + sel.target + ' وحدات' : 'الهدف: ما في هدف خاص');
    student.push('المواضيع اللي بدو يراجعها: ' + (sel.all ? 'كل المواضيع' : (picked.length ? listOfTitles(picked.map(function (e) { return e.topic; })) : 'ما حدّد، اسأله')));
    student.push('الوضع اللي اختاره: ' + MODES[mode].chosen);

    /* == المصادر == */
    const clean = mode === 'plan' ? function (text) { return text; } : withoutIds;
    const sourceLines = (section('المصادر') ? section('المصادر').lines : []).filter(function (line, i, all) {
      return !(line === '' && i === all.length - 1);
    }).map(function (line) {
      let out = line.replace(/^- مرفق:/, '- تحت:');
      if (/كلمة\s*"ملف"/.test(out) || out.indexOf('ملف') !== -1) out = '- ما تقول للطالب "المرفق" ولا اسم أي مصدر. قول "منهاجك".';
      if (mode !== 'plan' && ID.test(out)) out = '- ما تكتب أرقام المواضيع للطالب.';
      return out;
    });
    const sources = sourceLines.slice();
    sources.push('');
    levels.forEach(function (level, index) {
      sources.push('-- منهاج الطالب' + (index ? ' (مستوى الهدف)' : '') + ': ' + clean(level.title) + ' --');
      sources.push(clean(level.notes));
    });
    sources.push('');
    sources.push('-- المواضيع المختارة --');
    if (picked.length) {
      picked.forEach(function (entry) { sources.push('\n' + topicBlock(entry.topic, mode)); });
    } else sources.push('(ما حدّد الطالب مواضيع)');
    const patterns = patternsText(subject, found.grade.name, target ? [sel.units, sel.target] : [sel.units], mode);
    if (patterns) {
      sources.push('');
      sources.push('-- نمط أسئلة البجروت لمستواك --');
      sources.push(patterns);
    }
    let missing = false;
    if (mode !== 'plan') {
      const withExample = picked.find(function (entry) { return entry.topic.example; });
      if (withExample) {
        sources.push('');
        sources.push('-- مثال على الشكل، ما تعيده (موضوع: ' + withExample.topic.title + ') --');
        sources.push(withExample.topic.example);
      } else if (picked.length) missing = true;
    }

    /* the rest of the base prompt, with the chosen mode and its first move */
    const out = [title, ''];
    sections.forEach(function (s) {
      if (out[out.length - 1] !== '') out.push('');
      out.push('== ' + s.name + ' ==');
      if (s.name === 'الطالب') out.push.apply(out, student);
      else if (s.name === 'المصادر') out.push.apply(out, sources);
      else {
        const body = s.lines.slice();
        if (s === sections[sections.length - 1]) {
          /* the last section holds the closing line "ابدأ بسؤال الطالب ..." */
          for (let i = body.length - 1; i >= 0; i--) {
            if (/^ابدأ/.test(body[i])) body[i] = MODES[mode].start;
          }
        }
        out.push.apply(out, mode !== 'plan' ? body.map(function (line) { return ID.test(line) ? withoutIds(line) : line; }) : body);
      }
    });
    let text = out.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n';
    if (mode !== 'plan') text = withoutIds(text);
    return { text: text, length: text.length, max: MAX_LENGTH, tooLong: text.length > MAX_LENGTH, missingExample: missing, topics: picked.length };
  }

  return { buildPrompt: buildPrompt, findLevel: findLevel, MODES: MODES, MAX_LENGTH: MAX_LENGTH };
});
