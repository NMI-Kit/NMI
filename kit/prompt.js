/* Builds the prompt the student pastes into ChatGPT, Claude or Gemini.
   Pure functions: no DOM, no network. Used by app.js in the page and by the node tests. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NMIPrompt = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* Longest prompt we are happy to send, in characters. The biggest whole level (5 units, every topic) is about
     14,700, so one level with every topic fits. 15,500 characters is about 5,500 tokens in Arabic: a free-tier chat
     takes it, a phone pastes it without trouble, and the model still follows the rules at the top instead of
     drowning in text. A whole own level plus a whole target level is about 16,500 and gets the warning. */
  const MAX_LENGTH = 15500;

  /* Topics the student adds by hand: at most 5, each at most 60 characters, plain text only. */
  const MAX_CUSTOM = 5;
  const MAX_CUSTOM_LENGTH = 60;

  const MODES = {
    explain: {
      label: 'افهم', description: 'شرح موضوع خطوة خطوة.', chosen: 'افهم',
      start: 'ابدأ بسؤال الطالب: "أي موضوع بدك أشرحلك؟"'
    },
    practice: {
      label: 'تدرّب', description: 'سؤال بنمط الامتحان، قسم قسم، وبيصحّح حلك.', chosen: 'تدرّب',
      start: 'ابدأ مباشرة بسؤال جديد بنمط الامتحان على موضوع من اللي اختارهم الطالب: القصة والقسم أ بس، واستنى حله.'
    },
    mock: {
      label: 'امتحان تجريبي', description: 'امتحان كامل على المواضيع المختارة، وعلامة من 100 بالآخر.', chosen: 'امتحان تجريبي',
      start: 'ابدأ مباشرة بالامتحان التجريبي على المواضيع اللي اختارها الطالب: كل الأسئلة مرة وحدة، مع علامة كل قسم ووقت مقترح.'
    },
    plan: {
      label: 'خطة', description: 'خطة مراجعة لامتحانك بالأيام.', chosen: 'خطة',
      start: 'ابدأ بسؤال الطالب: "إمتى امتحانك؟ وكم ساعة بتقدر تدرس باليوم؟" وبعدين اعمل الخطة.'
    }
  };
  const MODE_ORDER = ['explain', 'practice', 'mock', 'plan'];

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

  /* No topic id ever reaches the student's prompt: the tutor names topics, it never numbers them. */
  function withoutIds(text) {
    return text.replace(ID_IN_PARENS, '').replace(BARE_ID, 'موضوع تاني');
  }

  /* control characters and invisible direction marks (U+2028 and U+2029 are caught by the whitespace step) */
  const HIDDEN = /[\u0000-\u001f\u007f-\u009f\u200e-\u200f\u202a-\u202e\u2066-\u2069]/g;

  /* One line of plain text: no line breaks, no control characters, single spaces, at most 60 characters. */
  function cleanTopic(text) {
    return String(text == null ? '' : text)
      .replace(HIDDEN, ' ')
      .replace(/\s+/g, ' ').trim().slice(0, MAX_CUSTOM_LENGTH).trim();
  }

  /* The list of topics the student added: cleaned, no empty, no duplicates, at most 5. */
  function cleanCustom(list) {
    const seen = new Set();
    const out = [];
    (Array.isArray(list) ? list : []).forEach(function (item) {
      const text = cleanTopic(item);
      const key = text.toLowerCase();
      if (text && !seen.has(key) && out.length < MAX_CUSTOM) { seen.add(key); out.push(text); }
    });
    return out;
  }

  /* The exam patterns of the student's own level: the general rules, the form sections of the level (a form written
     for one grade, like the 12th-grade form, only for that grade) and "how the tutor writes a question". */
  function patternsText(subject, gradeName, units) {
    const p = subject.patterns;
    if (!p) return '';
    const parts = [];
    if (p.general) parts.push(p.general);
    (p.levels[String(units)] || []).forEach(function (section) {
      if (!section.grade || section.grade === gradeName) parts.push(section.text);
    });
    if (p.howto) parts.push(p.howto);
    return parts.filter(Boolean).join('\n\n');
  }

  function topicBlock(topic) {
    const body = withoutIds(topic.text);
    return body ? '### ' + topic.title_full + '\n' + body : '### ' + topic.title_full;
  }

  function splitSections(base) {
    /* "== اسم ==" lines start a section; returns [{name, lines}] and the text before the first one. */
    const out = [];
    const head = [];
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

  function titles(topics) {
    return topics.map(function (t) { return t.title; }).join('، ');
  }

  /* sel: { subject, grade, units, target (units or null), topics (ids of the level or of the target level),
            all (every topic of the student's own level), custom (topics the student wrote), mode }
     Returns { text, length, tooLong, max, missingExample, topics, custom } or null when the level does not exist. */
  function buildPrompt(data, sel) {
    const mode = MODES[sel.mode] ? sel.mode : 'explain';
    const found = findLevel(data, sel.subject, sel.grade, sel.units);
    if (!found) return null;
    const subject = found.subject;
    const own = found.level;
    const targetFound = sel.target && Number(sel.target) > Number(sel.units) ? findLevel(data, sel.subject, sel.grade, sel.target) : null;
    const target = targetFound ? targetFound.level : null;

    /* the "all topics" choice is about the student's own level only; the target level's topics are picked one by one */
    const chosenIds = new Set(sel.topics || []);
    const pickedOwn = own.topics.filter(function (t) { return sel.all || chosenIds.has(t.id); });
    const pickedTarget = target ? target.topics.filter(function (t) { return chosenIds.has(t.id); }) : [];
    const custom = cleanCustom(sel.custom);

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
    const named = [];
    if (sel.all) named.push('كل المواضيع');
    else if (pickedOwn.length) named.push(titles(pickedOwn));
    if (pickedTarget.length) named.push('من مستوى الهدف: ' + titles(pickedTarget));
    if (custom.length) named.push('وزاد مواضيع بنفسه (تحت)');
    student.push('المواضيع اللي بدو يراجعها: ' + (named.length ? named.join('، ') : 'ما حدّد، اسأله'));
    student.push('الوضع اللي اختاره: ' + MODES[mode].chosen);

    /* == المصادر == */
    const sourceLines = (section('المصادر') ? section('المصادر').lines : []).filter(function (line, i, all) {
      return !(line === '' && i === all.length - 1);
    }).map(function (line) {
      let out = line.replace(/^- مرفق:/, '- تحت:');
      if (out.indexOf('ملف') !== -1) out = '- ما تقول للطالب "المرفق" ولا اسم أي مصدر. قول "منهاجك".';
      if (ID.test(out)) out = '- ما تكتب أرقام المواضيع للطالب.';
      return out;
    });
    const sources = sourceLines.slice();
    sources.push('');
    sources.push('-- منهاج الطالب: ' + withoutIds(own.title) + ' --');
    sources.push(withoutIds(own.notes));
    sources.push('');
    sources.push('-- المواضيع المختارة --');
    if (pickedOwn.length) {
      pickedOwn.forEach(function (topic) { sources.push('\n' + topicBlock(topic)); });
    } else sources.push('(ما اختار الطالب مواضيع من منهاجه)');
    if (target) {
      sources.push('');
      sources.push('-- مواضيع مستوى الهدف (' + sel.target + ' وحدات) --');
      if (pickedTarget.length) pickedTarget.forEach(function (topic) { sources.push('\n' + topicBlock(topic)); });
      else sources.push('(ما اختار الطالب مواضيع من مستوى الهدف)');
    }
    if (custom.length) {
      sources.push('');
      sources.push('-- مواضيع زادها الطالب بنفسه (مش من منهاجه) --');
      custom.forEach(function (text) { sources.push('- ' + text); });
      sources.push('اشرحها بمستوى الطالب. ما تحكي إنها من منهاجه. إذا الموضوع أعلى من مستواه، أو مش رياضيات، أو مذكور تحت "خارج المنهاج"، قله بصراحة.');
    }
    const patterns = patternsText(subject, found.grade.name, sel.units);
    if (patterns) {
      sources.push('');
      sources.push('-- دليل أنماط الامتحانات لمستواك --');
      sources.push(patterns);
    }
    let missing = false;
    const withExample = pickedOwn.concat(pickedTarget).find(function (topic) { return topic.example; });
    if (mode !== 'plan') {
      if (withExample) {
        sources.push('');
        sources.push('-- مثال على الشكل، ما تعيده (موضوع: ' + withExample.title + ') --');
        sources.push(withExample.example);
      } else if (pickedOwn.length + pickedTarget.length) missing = true;
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
        out.push.apply(out, body);
      }
    });
    const text = withoutIds(out.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n');
    return {
      text: text, length: text.length, max: MAX_LENGTH, tooLong: text.length > MAX_LENGTH, missingExample: missing,
      topics: pickedOwn.length + pickedTarget.length, custom: custom.length
    };
  }

  return {
    buildPrompt: buildPrompt, findLevel: findLevel, cleanCustom: cleanCustom, cleanTopic: cleanTopic,
    MODES: MODES, MODE_ORDER: MODE_ORDER, MAX_LENGTH: MAX_LENGTH, MAX_CUSTOM: MAX_CUSTOM, MAX_CUSTOM_LENGTH: MAX_CUSTOM_LENGTH
  };
});
