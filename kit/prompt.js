/* Builds the prompt the student pastes into ChatGPT, Claude or Gemini.
   Pure functions: no DOM, no network. Used by app.js in the page and by the node tests.
   The prompt is built in the language of the page: Arabic (the original, texts below), Hebrew or English (the translated
   files of kit/ and curriculum/, put in data.json as data.langs.he / data.langs.en by tools/build_kit.py, with their own
   `texts`). The code does not change from one language to the other: only the texts do. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NMIPrompt = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* Longest prompt we are happy to send, in characters. The biggest whole level (grade 10, 5 units, every topic) with
     any set of modes is about 18,250 in Arabic and 18,350 in Hebrew (the section of teaching methods and the tone rules
     add about 2,200), so one level with every topic fits. 19,050 characters is about 6,700 tokens: a free-tier chat
     takes it, a phone pastes it without trouble, and the model still follows the rules at the top instead of drowning
     in text. English has more letters for the same content (about 40% more characters, about the same tokens): the
     biggest English prompt is about 26,700 (with the teacher's file), and its limit is 27,000. A prompt that is longer
     (a whole level with a long mistakes section, or a whole own level plus a whole target level) is not refused: the
     page warns the student. */
  const MAX_LENGTH = 19050;
  const MAX_LENGTH_BY_LANGUAGE = { ar: MAX_LENGTH, he: MAX_LENGTH, en: 27000 };

  /* Topics the student adds by hand: at most 5, each at most 60 characters, plain text only. */
  const MAX_CUSTOM = 5;
  const MAX_CUSTOM_LENGTH = 60;

  /* The student's note to the tutor: one line of plain text, at most 200 characters. */
  const MAX_NOTE = 200;

  /* The student's teacher gave him an old exam or a worksheet: the student attaches the photos in his own app,
     nothing is uploaded to our site. Only for the modes in which the tutor writes questions. */
  const TEACHER_FILE_TEXT = 'الطالب رفعلك صورة أو ملف لامتحان قديم أو ورقة عمل من أستاذه. أول إشي: حلّل شكل الأسئلة باختصار (المواضيع، وعدد الأقسام، ونوع الطلبات، ومستوى الصعوبة)، واسأله إذا التحليل صح. بعدها اكتب أسئلة جديدة على نفس الشكل بالضبط، بأرقام وقصص جديدة. شكل أستاذه أهم من دليل الأنماط. ما تعيد أسئلة الورقة نفسها.';
  const NOTE_RULE = 'اتبع هالملاحظة بطريقة الشرح والأمثلة والتركيز. إلا إذا بتطلب تعطيه الحل بوضع التدريب أو الامتحان قبل ما يحاول، أو بتطلب إشي برا منهاجه: ساعتها قله بلطف ليش لأ، وكمّل حسب القواعد.';

  /* The first move of every mode is the closing line of the prompt. With the teacher's file the tutor first asks for it,
     analyses its shape, and only then starts. */
  const ASK_FOR_THE_FILE = 'إذا الطالب ما رفع الملف، اطلبه منه أول. بعد ما يرفعه: حلّل شكل الأسئلة واسأله إذا التحليل صح، وبعدها ';
  /* The tables of the guide describe exams that cover more than one grade: only their shape is for the student. */
  const PATTERNS_NOTE = 'الجداول بتوصف امتحانات بتغطي أكتر من صف. استعمل بس شكل الأسئلة (القصة، والأقسام، ونوع الطلبات)، وخلّي المحتوى والصعوبة من مواضيع الطالب المختارة ومن صفه بس.';
  /* The student chose the target topics on purpose, to move up a level: the notes of his own level may say that some of
     them are outside his curriculum, and the tutor must not refuse them because of that. */
  const TARGET_NOTE = 'الطالب اختار هالمواضيع قصداً عشان ينتقل لمستوى أعلى. علّمها عادي، حتى لو مكتوب فوق إنها خارج منهاج مستواه.';
  /* Said right after the "## الامتحان" section of the notes, which is only in the plan mode. */
  const EXAM_SECTION_NOTE = 'هاي المعلومات إلك عشان تبني الخطة. ما تذكر كلمة بجروت أو أرقام الاستمارات للطالب، إلا إذا سأل عنها أو حكى إن امتحانه بجروت.';
  /* "افهم" with more topics than this: the tutor asks which one to start with, instead of picking the first. */
  const MAX_DIRECT_START = 3;

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
  const WARMUP_START = 'ابدأ بسؤال إحماء سريع واحد على غلطة من "غلطات من جلسات قبل" فوق، وانتظر جوابه. بعدها ';
  const CUSTOM_NOTE = 'هاي مواضيع كتبها الطالب بنفسه. ممكن تكون من منهاجه بكلام تاني، أو من الإعدادية، أو من مستوى أعلى. إذا من منهاجه، اربطها بالموضوع المناسب. إذا من مستوى أعلى أو مذكورة تحت \'خارج المنهاج\'، قله بصراحة قبل ما تشرح. إذا مش رياضيات، قله.';
  const MAX_MISTAKES = 600;

  /* Every text the code adds to the prompt, in Arabic. {name} is filled by the code. The Hebrew and English tables are in
     kit/prompt_texts.he.json and kit/prompt_texts.en.json (the same keys, tested) and arrive in data.langs[lang].texts.
     Arabic is the original: its prompt is the same, character for character, as before the translations. */
  const ARABIC_TEXTS = {
    names: { student: 'الطالب', sources: 'المصادر', teaching: 'طريقة التعليم' },
    startPrefix: '^ابدأ',
    warmupStartPattern: '^ابدأ (مباشرة|بسؤال جديد)',
    modeLabels: { explain: 'افهم', practice: 'تدرّب', mock: 'امتحان تجريبي', plan: 'خطة' },
    topicsJoin: '، ',
    startExplainChoose: 'ابدأ بسؤال الطالب: أي موضوع من اللي اختارهم بدك نبلّش فيه؟ (المواضيع: {topics})',
    startExplain: 'ابدأ مباشرة بشرح {topic}.',
    startExplainNone: 'ابدأ بسؤال الطالب: "أي موضوع بدك أشرحلك؟"',
    startPractice: 'ابدأ مباشرة بسؤال جديد بنمط الامتحان على {topic}: القصة والقسم أ بس، واستنى.',
    startPracticeNone: 'ابدأ بسؤال الطالب: "أي موضوع بدك تتدرّب عليه؟"',
    startPracticeFile: 'ابدأ بسؤال جديد بنفس الشكل على {topic}: القصة والقسم أ بس، واستنى.',
    practiceFileNoTopic: 'الموضوع اللي بيختاره الطالب',
    startMock: 'ابدأ مباشرة بالامتحان التجريبي القصير على المواضيع المختارة.',
    startMockNone: 'ابدأ بسؤال الطالب: "على أي مواضيع بدك الامتحان؟"',
    startMockFile: 'اعطيه امتحان تجريبي قصير بنفس الشكل على المواضيع المختارة.',
    startPlan: 'ابدأ بسؤال الطالب: إمتى امتحانك، وكم ساعة بتقدر تدرس باليوم؟',
    askForFile: ASK_FOR_THE_FILE,
    patternsNote: PATTERNS_NOTE,
    targetNote: TARGET_NOTE,
    examSectionNote: EXAM_SECTION_NOTE,
    teacherFileText: TEACHER_FILE_TEXT,
    noteRule: NOTE_RULE,
    logRule: LOG_RULE,
    mistakesRule: MISTAKES_RULE,
    warmupStart: WARMUP_START,
    customNote: CUSTOM_NOTE,
    subjectLine: 'المادة: {value}',
    gradeLine: 'الصف: {value}',
    unitsLine: 'الوحدات: {value}',
    goalLine: 'الهدف: الانتقال من {from} لـ {to} وحدات',
    goalNone: 'الهدف: ما في هدف خاص',
    topicsLine: 'المواضيع اللي بدو يراجعها: {value}',
    allTopics: 'كل المواضيع',
    noTopics: 'ما حدّد، اسأله',
    modeLine: 'الوضع اللي اختاره: {value}',
    modesSeveral: 'الطالب اختار: {labels}. ابدأ بأول وحدة بس. كل رد بوضع واحد بس. لما تخلص الوضع، اسأله إذا جاهز للي بعده، وما تنتقل قبل ما يجاوب.',
    studentLanguage: [],
    secLog: '== ملخص الجلسة للعدّة ==',
    secMistakes: '== غلطات من جلسات قبل ==',
    secFile: '== ملف من الأستاذ ==',
    secNote: '== ملاحظة من الطالب ==',
    srcCurriculum: '-- منهاج الطالب: {title} --',
    srcPicked: '-- المواضيع المختارة --',
    srcTarget: '-- مواضيع مستوى الهدف ({units} وحدات) --',
    srcCustom: '-- مواضيع كتبها الطالب بنفسه --',
    srcPatterns: '-- دليل أنماط الامتحانات لمستواك --',
    srcExample: '-- مثال على الشكل، ما تعيده (موضوع: {topic}) --',
    srcAttached: '- مرفق:',
    srcBelow: '- تحت:',
    srcGuide: '، ودليل أنماط أسئلة الامتحانات',
    srcFileWord: 'ملف',
    srcFileLine: '- ما تقول للطالب "المرفق" ولا اسم أي مصدر. قول "منهاجك".',
    srcIdLine: '- ما تكتب أرقام المواضيع للطالب.',
    mathWord: 'رياضيات',
    anotherTopic: 'موضوع تاني',
    examHeading: '## الامتحان',
    fiveUnitsLine: '   - **5 وحدات كمان:**'
  };

  /* The page in Hebrew or English: a first line before everything and a last line after the closing line, in the language
     of the student, because the models answer in the language of the last lines they read. */
  const STUDENT_LANGUAGE = { he: 'עברית', en: 'English' };
  const LANGUAGE_FIRST_LINE = {
    he: 'חשוב: כל התשובות שלך לתלמיד יהיו בעברית בלבד, מההודעה הראשונה.',
    en: 'Important: every reply to the student must be in English only, from the first message.'
  };
  const LANGUAGE_LAST_LINE = { he: 'התחל עכשיו, בעברית בלבד.', en: 'Start now, in English only.' };

  /* The name of a topic between « » in the sentences of the prompt. */
  function quoted(name) { return '«' + name + '»'; }

  /* "text {a} {b}" with the values: the code never builds a sentence by hand. */
  function fill(template, values) {
    return String(template).replace(/\{(\w+)\}/g, function (all, key) { return key in values ? values[key] : all; });
  }

  /* The modes: the label of the Arabic prompt is the one the tests and the page know. */
  const MODES = {
    explain: { label: 'افهم', chosen: 'افهم' },
    practice: { label: 'تدرّب', chosen: 'تدرّب' },
    mock: { label: 'امتحان تجريبي', chosen: 'امتحان تجريبي' },
    plan: { label: 'خطة', chosen: 'خطة' }
  };
  const MODE_ORDER = ['explain', 'practice', 'mock', 'plan'];  // the order of the buttons on the page
  /* the order in the prompt, whatever the order of the ticks: the plan first, then understand, practice, mock exam */
  const PROMPT_ORDER = ['plan', 'explain', 'practice', 'mock'];

  /* The closing line of the prompt: the first move of the first mode. `first` is the name of the first chosen topic, or
     '' when the student chose nothing (then the tutor asks). `all` the names of every chosen topic. */
  function startLine(T, mode, first, all, teacherFile) {
    if (mode === 'explain') {
      if (all && all.length > MAX_DIRECT_START) return fill(T.startExplainChoose, { topics: all.map(quoted).join(T.topicsJoin) });
      return first ? fill(T.startExplain, { topic: quoted(first) }) : T.startExplainNone;
    }
    if (mode === 'practice') {
      if (teacherFile) return T.askForFile + fill(T.startPracticeFile, { topic: first ? quoted(first) : T.practiceFileNoTopic });
      return first ? fill(T.startPractice, { topic: quoted(first) }) : T.startPracticeNone;
    }
    if (mode === 'mock') {
      if (teacherFile) return T.askForFile + T.startMockFile;
      return first ? T.startMock : T.startMockNone;
    }
    return T.startPlan;
  }

  /* the NMI-LOG rule is in the prompt with any mode except a plan alone */
  function hasLogRule(modes) {
    return modes.some(function (m) { return m !== 'plan'; });
  }
  /* The teaching methods (retrieval, spacing, interleaving ...): a section of the base prompt, in every prompt except a
     plan alone. With old mistakes in the prompt, "افهم" and "تدرّب" start with a quick warm-up question on one of them. */
  function hasTeachingMethods(modes) {
    return modes.some(function (m) { return m !== 'plan'; });
  }
  const WARMUP_MODES = { explain: true, practice: true };

  /* The modes the student ticked, in the order of the prompt. One mode in `sel.mode` still works; nothing ticked
     is treated as "افهم" (the page does not allow it). */
  function chosenModes(sel) {
    const raw = Array.isArray(sel.modes) ? sel.modes : (sel.mode ? [sel.mode] : []);
    const ticked = PROMPT_ORDER.filter(function (m) { return MODES[m] && raw.indexOf(m) !== -1; });
    return ticked.length ? ticked : ['explain'];
  }

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
  function withoutIds(text, T) {
    return text.replace(ID_IN_PARENS, '').replace(BARE_ID, (T || ARABIC_TEXTS).anotherTopic);
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

  /* The guide is still called "Bagrut patterns" in the curriculum folder; the Arabic prompt says "exam" (school exams).
     The Hebrew and English guides already say "exam". */
  function asExam(text) {
    return text.replace(/البجروت/g, 'الامتحان').replace(/بجروت/g, 'امتحان');
  }

  /* The notes of a level are "## heading" sections. The exam section (form numbers, "Bagrut at the end of grade 11")
     is only for the plan mode. */
  function notesText(notes, mode, T) {
    const parts = [];
    notes.split(/\n\n(?=## )/).forEach(function (part) {
      if (part.split('\n')[0].trim() !== T.examHeading) { parts.push(part); return; }
      if (mode !== 'plan') return;
      /* the exam section talks about the Bagrut (form numbers): it is there to build the plan, and the tutor is told
         right after it not to say the word to the student */
      parts.push(part, T.examSectionNote);
    });
    return parts.join('\n\n').trim();
  }

  /* The exam patterns of the student's own level: the general rules, the form sections of the level (a form written
     for one grade, like the 12th-grade form, only for that grade) and "how the tutor writes a question". The line of the
     general rules about what 5 units also ask (prove, sketch, a parameter) is only in a 5-unit prompt. */
  function patternsText(subject, gradeName, units, arabic, T) {
    const p = subject.patterns;
    if (!p) return '';
    const parts = [];
    if (p.general) {
      parts.push(Number(units) === 5 ? p.general : p.general.split('\n').filter(function (line) { return line.indexOf(T.fiveUnitsLine) !== 0; }).join('\n'));
    }
    (p.levels[String(units)] || []).forEach(function (section) {
      if (!section.grade || section.grade === gradeName) parts.push(section.text);
    });
    if (p.howto) parts.push(p.howto);
    const text = parts.filter(Boolean).join('\n\n');
    return arabic ? asExam(text) : text;
  }

  function topicBlock(topic, T) {
    const body = withoutIds(topic.text, T);
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

  /* The data and the texts of the language of the page: Hebrew and English come with their own data (data.langs); a data
     file without them (an old one) gives the Arabic prompt. */
  function languageData(data, language) {
    if ((language === 'he' || language === 'en') && data.langs && data.langs[language] && data.langs[language].texts) {
      return { lang: language, data: data.langs[language], T: data.langs[language].texts };
    }
    return { lang: 'ar', data: data, T: ARABIC_TEXTS };
  }

  /* sel: { subject, grade, units, target (units or null), topics (ids of the level or of the target level),
            all (every topic of the student's own level), custom (topics the student wrote), modes (the ticked modes;
            `mode` with one mode still works), mistakes (the "غلط:" lines of the old sessions),
            teacherFile (true: he has an old exam or worksheet from his teacher), note (a note to the tutor),
            language (the language of the page: 'ar', 'he' or 'en'; the prompt is built in that language) }
     Returns { text, length, tooLong, max, missingExample, topics, custom } or null when the level does not exist. */
  function buildPrompt(arabicData, sel) {
    const chosen = languageData(arabicData, sel.language);
    const data = chosen.data;
    const T = chosen.T;
    const modes = chosenModes(sel);
    const mode = modes[0];  // the first one starts the session
    const labels = modes.map(function (m) { return T.modeLabels[m]; });
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
    if (subject.name && subject.id !== 'math') title = title.replace(T.mathWord, subject.name);

    /* == الطالب == : every chosen topic by name, the ones from the list and the ones the student wrote */
    const student = [];
    student.push(fill(T.subjectLine, { value: subject.name }));
    student.push(fill(T.gradeLine, { value: found.grade.name }));
    student.push(fill(T.unitsLine, { value: sel.units }));
    student.push(target ? fill(T.goalLine, { from: sel.units, to: sel.target }) : T.goalNone);
    const named = (sel.all ? [T.allTopics] : names(pickedOwn)).concat(names(pickedTarget), custom);
    student.push(fill(T.topicsLine, { value: named.length ? named.join(T.topicsJoin) : T.noTopics }));
    student.push(fill(T.modeLine, { value: labels.join(' + ') }));
    if (modes.length > 1) student.push(fill(T.modesSeveral, { labels: labels.join(' + ') }));

    /* a page in Hebrew or English: the language of the student, once (nothing for Arabic) */
    const otherLanguage = chosen.lang !== 'ar';
    T.studentLanguage.forEach(function (line) { student.push(line); });

    /* what the tutor starts with: the first topic of the student, in the order of the list, then the ones he wrote */
    const everyName = names(pickedOwn.concat(pickedTarget)).concat(custom);
    const first = everyName[0] || '';

    const patterns = guide ? patternsText(subject, found.grade.name, sel.units, chosen.lang === 'ar', T) : '';

    /* == المصادر == : a section that would be empty is not written at all, not even its heading */
    const sourceSection = section(T.names.sources);
    const sourceLines = (sourceSection ? sourceSection.lines : []).filter(function (line, i, all) {
      return !(line === '' && i === all.length - 1);
    }).map(function (line) {
      let out = line.indexOf(T.srcAttached) === 0 ? T.srcBelow + line.slice(T.srcAttached.length) : line;
      if (!patterns) out = out.replace(T.srcGuide, '');  // the guide is not in this prompt
      if (out.indexOf(T.srcFileWord) !== -1) out = T.srcFileLine;
      if (ID.test(out)) out = T.srcIdLine;
      return out;
    });
    const sources = sourceLines.slice();
    const notes = notesText(own.notes, withPlan ? 'plan' : mode, T);
    if (notes) {
      sources.push('');
      sources.push(fill(T.srcCurriculum, { title: withoutIds(own.title, T) }));
      sources.push(withoutIds(notes, T));
    }
    if (pickedOwn.length) {
      sources.push('');
      sources.push(T.srcPicked);
      pickedOwn.forEach(function (topic) { sources.push('\n' + topicBlock(topic, T)); });
    }
    if (pickedTarget.length) {
      sources.push('');
      sources.push(fill(T.srcTarget, { units: sel.target }));
      sources.push(T.targetNote);
      pickedTarget.forEach(function (topic) { sources.push('\n' + topicBlock(topic, T)); });
    }
    if (custom.length) {
      sources.push('');
      sources.push(T.srcCustom);
      custom.forEach(function (text) { sources.push('- ' + text); });
      sources.push(T.customNote);
    }
    if (patterns) {
      sources.push('');
      sources.push(T.srcPatterns);
      sources.push(T.patternsNote);
      sources.push('');
      sources.push(patterns);
    }
    let missing = false;
    if (guide) {
      const withExample = pickedOwn.concat(pickedTarget).find(function (topic) { return topic.example; });
      if (withExample) {
        sources.push('');
        sources.push(fill(T.srcExample, { topic: quoted(withExample.title) }));
        sources.push(withExample.example);
      } else if (pickedOwn.length + pickedTarget.length) missing = true;
    }

    /* the rest of the base prompt, with the chosen mode and its first move */
    const out = otherLanguage ? [LANGUAGE_FIRST_LINE[chosen.lang], '', title, ''] : [title, ''];
    const startPrefix = new RegExp(T.startPrefix);
    const warmupPattern = new RegExp(T.warmupStartPattern);
    sections.forEach(function (s) {
      if (s.name === T.names.teaching && !hasTeachingMethods(modes)) return;  // a plan alone has no section of teaching methods
      if (out[out.length - 1] !== '') out.push('');
      out.push('== ' + s.name + ' ==');
      if (s.name === T.names.student) out.push.apply(out, student);
      else if (s.name === T.names.sources) out.push.apply(out, sources);
      else {
        const body = s.lines.slice();
        if (s === sections[sections.length - 1]) {
          /* the last section holds the closing line "ابدأ بسؤال الطالب ...". Before it: the sections of the teacher's
             file and of the student's note, when there are any. With the teacher's file the tutor first asks for it. */
          const extra = [];
          if (hasLogRule(modes)) extra.push(T.secLog, ...T.logRule, '');
          if (mistakes.length) extra.push(T.secMistakes, ...mistakes, T.mistakesRule, '');
          if (teacherFile) extra.push(T.secFile, T.teacherFileText, '');
          if (note) extra.push(T.secNote, note, T.noteRule, '');
          for (let i = body.length - 1; i >= 0; i--) {
            if (startPrefix.test(body[i])) {
              let line = startLine(T, mode, first, everyName, teacherFile && (mode === 'practice' || mode === 'mock'));
              /* old mistakes in the prompt: the warm-up question of the teaching methods comes before the first move */
              if (mistakes.length && !teacherFile && WARMUP_MODES[mode] && warmupPattern.test(line)) line = T.warmupStart + line;
              body.splice(i, 1, ...extra, line);
              break;
            }
          }
        }
        out.push.apply(out, body);
      }
    });
    if (otherLanguage) out.push('', LANGUAGE_LAST_LINE[chosen.lang]);  // after the closing line
    const text = withoutIds(out.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n', T);
    return {
      text: text, length: text.length, max: MAX_LENGTH_BY_LANGUAGE[chosen.lang], tooLong: text.length > MAX_LENGTH_BY_LANGUAGE[chosen.lang], missingExample: missing,
      topics: pickedOwn.length + pickedTarget.length, custom: custom.length, teacherFile: teacherFile, note: note.length > 0,
      modes: modes, mistakes: mistakes.length > 0
    };
  }

  return {
    buildPrompt: buildPrompt, findLevel: findLevel, cleanCustom: cleanCustom, cleanTopic: cleanTopic, cleanNote: cleanNote, MAX_NOTE: MAX_NOTE, WRITES_QUESTIONS: WRITES_QUESTIONS,
    MODES: MODES, MODE_ORDER: MODE_ORDER, PROMPT_ORDER: PROMPT_ORDER, chosenModes: chosenModes, cleanMistakes: cleanMistakes, LOG_RULE: LOG_RULE, MAX_MISTAKES: MAX_MISTAKES,
    MAX_DIRECT_START: MAX_DIRECT_START, PATTERNS_NOTE: PATTERNS_NOTE, TARGET_NOTE: TARGET_NOTE, EXAM_SECTION_NOTE: EXAM_SECTION_NOTE, MAX_LENGTH: MAX_LENGTH, MAX_LENGTH_BY_LANGUAGE: MAX_LENGTH_BY_LANGUAGE,
    MAX_CUSTOM: MAX_CUSTOM, MAX_CUSTOM_LENGTH: MAX_CUSTOM_LENGTH, ARABIC_TEXTS: ARABIC_TEXTS, LANGUAGE_FIRST_LINE: LANGUAGE_FIRST_LINE, LANGUAGE_LAST_LINE: LANGUAGE_LAST_LINE,
    STUDENT_LANGUAGE: STUDENT_LANGUAGE, fill: fill
  };
});
