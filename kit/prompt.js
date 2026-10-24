/* Builds the prompt the student pastes into ChatGPT, Claude or Gemini.
   Pure functions: no DOM, no network. Used by app.js in the page and by the node tests. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NMIPrompt = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* Longest prompt we are happy to send, in characters. The biggest whole level (grade 10, 5 units, every topic) with
     any set of modes is about 15,700, so one level with every topic fits. 16,000 characters is about 5,700 tokens in
     Arabic: a free-tier chat takes it, a phone pastes it without trouble, and the model still follows the rules at the
     top instead of drowning in text. A prompt that is longer (a whole level with a long mistakes section, or a whole own
     level plus a whole target level) is not refused: the page warns the student. */
  const MAX_LENGTH = 16000;

  /* Topics the student adds by hand: at most 5, each at most 60 characters, plain text only. */
  const MAX_CUSTOM = 5;
  const MAX_CUSTOM_LENGTH = 60;

  /* The student's note to the tutor: one line of plain text, at most 200 characters. */
  const MAX_NOTE = 200;

  /* The student's teacher gave him an old exam or a worksheet: the student attaches the photos in his own app,
     nothing is uploaded to our site. Only for the modes in which the tutor writes questions. */
  const TEACHER_FILE_TEXT = 'الطالب رفعلك صورة أو ملف لامتحان قديم أو ورقة عمل من أستاذه. أول إشي: حلّل شكل الأسئلة باختصار (المواضيع، وعدد الأقسام، ونوع الطلبات، ومستوى الصعوبة)، واسأله إذا التحليل صح. بعدها اكتب أسئلة جديدة على نفس الشكل بالضبط، بأرقام وقصص جديدة. شكل أستاذه أهم من دليل الأنماط. ما تعيد أسئلة الورقة نفسها.';
  const NOTE_RULE = 'اتبع هالملاحظة بطريقة الشرح والأمثلة والتركيز. إلا إذا بتطلب تعطيه الحل بوضع التدريب أو الامتحان قبل ما يحاول، أو بتطلب إشي برا منهاجه: ساعتها قله بلطف ليش لأ، وكمّل حسب القواعد.';

  /* The name of a topic between « » in the sentences of the prompt. */
  function quoted(name) { return '«' + name + '»'; }

  /* start(first): the closing line. `first` is the name of the first chosen topic, or '' when the student chose
     nothing (then the tutor asks). fileStart(first): the same, when the student has an old exam or a worksheet from
     his teacher: the tutor first asks for it, analyses its shape, and only then starts. */
  const ASK_FOR_THE_FILE = 'إذا الطالب ما رفع الملف، اطلبه منه أول. بعد ما يرفعه: حلّل شكل الأسئلة واسأله إذا التحليل صح، وبعدها ';
  const MODES = {
    explain: {
      label: 'افهم', description: 'شرح موضوع خطوة خطوة.', chosen: 'افهم',
      start: function (first, all) {
        if (all && all.length > MAX_DIRECT_START) {
          return 'ابدأ بسؤال الطالب: أي موضوع من اللي اختارهم بدك نبلّش فيه؟ (المواضيع: ' + all.map(quoted).join('، ') + ')';
        }
        return first ? 'ابدأ مباشرة بشرح ' + quoted(first) + '.' : 'ابدأ بسؤال الطالب: "أي موضوع بدك أشرحلك؟"';
      }
    },
    practice: {
      label: 'تدرّب', description: 'سؤال بنمط الامتحان، قسم قسم، وبيصحّح حلك.', chosen: 'تدرّب',
      start: function (first) {
        return first ? 'ابدأ مباشرة بسؤال جديد بنمط الامتحان على ' + quoted(first) + ': القصة والقسم أ بس، واستنى.'
          : 'ابدأ بسؤال الطالب: "أي موضوع بدك تتدرّب عليه؟"';
      },
      fileStart: function (first) {
        return ASK_FOR_THE_FILE + 'ابدأ بسؤال جديد بنفس الشكل على ' + (first ? quoted(first) : 'الموضوع اللي بيختاره الطالب') + ': القصة والقسم أ بس، واستنى.';
      }
    },
    mock: {
      label: 'امتحان تجريبي', description: 'امتحان كامل على المواضيع المختارة، وعلامة من 100 بالآخر.', chosen: 'امتحان تجريبي',
      start: function (first) {
        return first ? 'ابدأ مباشرة بالامتحان التجريبي كامل على المواضيع المختارة.'
          : 'ابدأ بسؤال الطالب: "على أي مواضيع بدك الامتحان؟"';
      },
      fileStart: function () {
        return ASK_FOR_THE_FILE + 'اعطيه امتحان تجريبي كامل بنفس الشكل على المواضيع المختارة.';
      }
    },
    plan: {
      label: 'خطة', description: 'خطة مراجعة لامتحانك بالأيام.', chosen: 'خطة',
      start: function () { return 'ابدأ بسؤال الطالب: إمتى امتحانك، وكم ساعة بتقدر تدرس باليوم؟'; }
    }
  };
  /* The tables of the guide describe exams that cover more than one grade: only their shape is for the student. */
  const PATTERNS_NOTE = 'الجداول بتوصف امتحانات بتغطي أكتر من صف. استعمل بس شكل الأسئلة (القصة، والأقسام، ونوع الطلبات)، وخلّي المحتوى والصعوبة من مواضيع الطالب المختارة ومن صفه بس.';
  /* The student chose the target topics on purpose, to move up a level: the notes of his own level may say that some of
     them are outside his curriculum, and the tutor must not refuse them because of that. */
  const TARGET_NOTE = 'الطالب اختار هالمواضيع قصداً عشان ينتقل لمستوى أعلى. علّمها عادي، حتى لو مكتوب فوق إنها خارج منهاج مستواه.';
  /* Said right after the "## الامتحان" section of the notes, which is only in the plan mode. */
  const EXAM_SECTION_NOTE = 'هاي المعلومات إلك عشان تبني الخطة. ما تذكر كلمة بجروت أو أرقام الاستمارات للطالب، إلا إذا سأل عنها أو حكى إن امتحانه بجروت.';
  /* "افهم" with more topics than this: the tutor asks which one to start with, instead of picking the first. */
  const MAX_DIRECT_START = 3;
  const MODE_ORDER = ['explain', 'practice', 'mock', 'plan'];  // the order of the buttons on the page
  /* the order in the prompt, whatever the order of the ticks: the plan first, then understand, practice, mock exam */
  const PROMPT_ORDER = ['plan', 'explain', 'practice', 'mock'];

  /* The modes the student ticked, in the order of the prompt. One mode in `sel.mode` still works; nothing ticked
     is treated as "افهم" (the page does not allow it). */
  function chosenModes(sel) {
    const raw = Array.isArray(sel.modes) ? sel.modes : (sel.mode ? [sel.mode] : []);
    const ticked = PROMPT_ORDER.filter(function (m) { return MODES[m] && raw.indexOf(m) !== -1; });
    return ticked.length ? ticked : ['explain'];
  }

  /* The mistakes log: the tutor ends a session with a summary that the student pastes into "سجلّي" of the kit. */
  const LOG_RULE = [
    'لما الطالب يحكي \'خلصت\'، أو بعد ملخص آخر سؤال، اكتب ملخص للعدّة جوّا code block، بهالشكل بالضبط:',
    'NMI-LOG',
    'المواضيع: ...',
    'ضبط: ...',
    'غلط: ... (كل غلطة بجملة قصيرة: شو الغلط وبأي موضوع)',
    'وقله: \'إذا بدك، انسخ هاد والصقه بالعدّة بصفحة سجلّي. مش إجباري، بس بيخلّيني أفحصك على غلطاتك بالمرة الجاية.\''
  ];
  const MISTAKES_RULE = 'خلال الجلسة، افحصه على هالغلطات بسؤال واحد على الأقل. ما تذكرها إلا إذا إلها علاقة بالسؤال.';
  const MAX_MISTAKES = 600;

  /* The exam patterns guide (and its example) only helps when the tutor writes questions. */
  const WRITES_QUESTIONS = { practice: true, mock: true };

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
  const HIDDEN = /[\u0000-\u001f\u007f-\u009f‎-‏‪-‮⁦-⁩]/g;

  /* One line of plain text: no line breaks, no control characters, single spaces, at most 60 characters. */
  function oneLine(text) {
    return String(text == null ? '' : text).replace(HIDDEN, ' ').replace(/\s+/g, ' ').trim();
  }

  function cleanTopic(text) {
    return oneLine(text).slice(0, MAX_CUSTOM_LENGTH).trim();
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

  /* The "غلط:" lines of the old sessions: one line each, plain text, at most 600 characters together. */
  function cleanMistakes(list) {
    const out = [];
    let used = 0;
    (Array.isArray(list) ? list : []).forEach(function (item) {
      const line = oneLine(item).replace(/^[=\s]+/, '');
      const room = MAX_MISTAKES - used - (out.length ? 1 : 0);
      if (!line || room < 12) return;
      const piece = line.slice(0, room).trim();
      out.push(piece);
      used += piece.length + (out.length > 1 ? 1 : 0);
    });
    return out;
  }

  /* The note of the student: one line, plain text, at most 200 characters, and it cannot open a section of the
     prompt (a line that starts with "==" is a section heading, so leading "=" signs are dropped). */
  function cleanNote(text) {
    return oneLine(text).replace(/^[=\s]+/, '').slice(0, MAX_NOTE).trim();
  }

  /* The guide is still called "Bagrut patterns" in the curriculum folder; the prompt says "exam" (school exams). */
  function asExam(text) {
    return text.replace(/البجروت/g, 'الامتحان').replace(/بجروت/g, 'امتحان');
  }

  /* The notes of a level are "## heading" sections. "## الامتحان" (form numbers, "Bagrut at the end of grade 11")
     is only for the plan mode. */
  function notesText(notes, mode) {
    const parts = [];
    notes.split(/\n\n(?=## )/).forEach(function (part) {
      if (part.split('\n')[0].trim() !== '## الامتحان') { parts.push(part); return; }
      if (mode !== 'plan') return;
      /* the exam section talks about the Bagrut (form numbers): it is there to build the plan, and the tutor is told
         right after it not to say the word to the student */
      parts.push(part, EXAM_SECTION_NOTE);
    });
    return parts.join('\n\n').trim();
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
    return asExam(parts.filter(Boolean).join('\n\n'));
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

  function names(topics) {
    return topics.map(function (t) { return t.title; });
  }

  /* sel: { subject, grade, units, target (units or null), topics (ids of the level or of the target level),
            all (every topic of the student's own level), custom (topics the student wrote), modes (the ticked modes;
            `mode` with one mode still works), mistakes (the "غلط:" lines of the old sessions),
            teacherFile (true: he has an old exam or worksheet from his teacher), note (a note to the tutor) }
     Returns { text, length, tooLong, max, missingExample, topics, custom } or null when the level does not exist. */
  function buildPrompt(data, sel) {
    const modes = chosenModes(sel);
    const mode = modes[0];  // the first one starts the session
    const labels = modes.map(function (m) { return MODES[m].chosen; });
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
    const note = cleanNote(sel.note);
    const guide = modes.some(function (m) { return WRITES_QUESTIONS[m] === true; });  // practice or the mock exam
    const withPlan = modes.indexOf('plan') !== -1;
    const teacherFile = sel.teacherFile === true && guide;
    const mistakes = cleanMistakes(sel.mistakes);

    const { head, sections } = splitSections(data.base_prompt);
    const section = function (name) { return sections.find(function (s) { return s.name === name; }); };
    let title = head.join('\n').trim();
    if (subject.name && subject.id !== 'math') title = title.replace('رياضيات', subject.name);

    /* == الطالب == : every chosen topic by name, the ones from the list and the ones the student wrote */
    const student = [];
    student.push('المادة: ' + subject.name);
    student.push('الصف: ' + found.grade.name);
    student.push('الوحدات: ' + sel.units);
    student.push(target ? 'الهدف: الانتقال من ' + sel.units + ' لـ ' + sel.target + ' وحدات' : 'الهدف: ما في هدف خاص');
    const named = (sel.all ? ['كل المواضيع'] : names(pickedOwn)).concat(names(pickedTarget), custom);
    student.push('المواضيع اللي بدو يراجعها: ' + (named.length ? named.join('، ') : 'ما حدّد، اسأله'));
    student.push('الوضع اللي اختاره: ' + labels.join(' + '));
    if (modes.length > 1) student.push('الطالب اختار: ' + labels.join(' + ') + '. ابدأ بأول وحدة. لما يخلص أو يطلب، انتقل للي بعدها.');

    /* what the tutor starts with: the first topic of the student, in the order of the list, then the ones he wrote */
    const everyName = names(pickedOwn.concat(pickedTarget)).concat(custom);
    const first = everyName[0] || '';

    const patterns = guide ? patternsText(subject, found.grade.name, sel.units) : '';

    /* == المصادر == : a section that would be empty is not written at all, not even its heading */
    const sourceLines = (section('المصادر') ? section('المصادر').lines : []).filter(function (line, i, all) {
      return !(line === '' && i === all.length - 1);
    }).map(function (line) {
      let out = line.replace(/^- مرفق:/, '- تحت:');
      if (!patterns) out = out.replace('، ودليل أنماط أسئلة الامتحانات', '');  // the guide is not in this prompt
      if (out.indexOf('ملف') !== -1) out = '- ما تقول للطالب "المرفق" ولا اسم أي مصدر. قول "منهاجك".';
      if (ID.test(out)) out = '- ما تكتب أرقام المواضيع للطالب.';
      return out;
    });
    const sources = sourceLines.slice();
    const notes = notesText(own.notes, withPlan ? 'plan' : mode);
    if (notes) {
      sources.push('');
      sources.push('-- منهاج الطالب: ' + withoutIds(own.title) + ' --');
      sources.push(withoutIds(notes));
    }
    if (pickedOwn.length) {
      sources.push('');
      sources.push('-- المواضيع المختارة --');
      pickedOwn.forEach(function (topic) { sources.push('\n' + topicBlock(topic)); });
    }
    if (pickedTarget.length) {
      sources.push('');
      sources.push('-- مواضيع مستوى الهدف (' + sel.target + ' وحدات) --');
      sources.push(TARGET_NOTE);
      pickedTarget.forEach(function (topic) { sources.push('\n' + topicBlock(topic)); });
    }
    if (custom.length) {
      sources.push('');
      sources.push('-- مواضيع كتبها الطالب بنفسه --');
      custom.forEach(function (text) { sources.push('- ' + text); });
      sources.push('هاي مواضيع كتبها الطالب بنفسه. ممكن تكون من منهاجه بكلام تاني، أو من الإعدادية، أو من مستوى أعلى. إذا من منهاجه، اربطها بالموضوع المناسب. إذا من مستوى أعلى أو مذكورة تحت \'خارج المنهاج\'، قله بصراحة قبل ما تشرح. إذا مش رياضيات، قله.');
    }
    if (patterns) {
      sources.push('');
      sources.push('-- دليل أنماط الامتحانات لمستواك --');
      sources.push(PATTERNS_NOTE);
      sources.push('');
      sources.push(patterns);
    }
    let missing = false;
    if (guide) {
      const withExample = pickedOwn.concat(pickedTarget).find(function (topic) { return topic.example; });
      if (withExample) {
        sources.push('');
        sources.push('-- مثال على الشكل، ما تعيده (موضوع: ' + quoted(withExample.title) + ') --');
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
          /* the last section holds the closing line "ابدأ بسؤال الطالب ...". Before it: the sections of the teacher's
             file and of the student's note, when there are any. With the teacher's file the tutor first asks for it. */
          const extra = [];
          if (modes.some(function (m) { return m !== 'plan'; })) extra.push('== ملخص الجلسة للعدّة ==', ...LOG_RULE, '');
          if (mistakes.length) extra.push('== غلطات من جلسات قبل ==', ...mistakes, MISTAKES_RULE, '');
          if (teacherFile) extra.push('== ملف من الأستاذ ==', TEACHER_FILE_TEXT, '');
          if (note) extra.push('== ملاحظة من الطالب ==', note, NOTE_RULE, '');
          for (let i = body.length - 1; i >= 0; i--) {
            if (/^ابدأ/.test(body[i])) {
              body.splice(i, 1, ...extra, teacherFile && MODES[mode].fileStart ? MODES[mode].fileStart(first) : MODES[mode].start(first, everyName));
              break;
            }
          }
        }
        out.push.apply(out, body);
      }
    });
    const text = withoutIds(out.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n');
    return {
      text: text, length: text.length, max: MAX_LENGTH, tooLong: text.length > MAX_LENGTH, missingExample: missing,
      topics: pickedOwn.length + pickedTarget.length, custom: custom.length, teacherFile: teacherFile, note: note.length > 0,
      modes: modes, mistakes: mistakes.length > 0
    };
  }

  return {
    buildPrompt: buildPrompt, findLevel: findLevel, cleanCustom: cleanCustom, cleanTopic: cleanTopic, cleanNote: cleanNote, MAX_NOTE: MAX_NOTE, WRITES_QUESTIONS: WRITES_QUESTIONS,
    MODES: MODES, MODE_ORDER: MODE_ORDER, PROMPT_ORDER: PROMPT_ORDER, chosenModes: chosenModes, cleanMistakes: cleanMistakes, LOG_RULE: LOG_RULE, MAX_MISTAKES: MAX_MISTAKES, MAX_DIRECT_START: MAX_DIRECT_START, PATTERNS_NOTE: PATTERNS_NOTE, TARGET_NOTE: TARGET_NOTE, EXAM_SECTION_NOTE: EXAM_SECTION_NOTE, MAX_LENGTH: MAX_LENGTH, MAX_CUSTOM: MAX_CUSTOM, MAX_CUSTOM_LENGTH: MAX_CUSTOM_LENGTH
  };
});
