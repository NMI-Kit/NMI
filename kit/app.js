/* NMI kit page: four steps (level, topics, mode, ready). The prompt itself is built by prompt.js. */
(function () {
  'use strict';

  var P = window.NMIPrompt;
  var L = window.NMILog;
  var APPS = [
    { name: 'ChatGPT', url: 'https://chatgpt.com/', host: 'chatgpt.com', path: '', package: 'com.openai.chatgpt' },
    { name: 'Claude', url: 'https://claude.ai/new', host: 'claude.ai', path: 'new', package: 'com.anthropic.claude' },
    { name: 'Gemini', url: 'https://gemini.google.com/app', host: 'gemini.google.com', path: 'app', package: 'com.google.android.apps.bard' }
  ];
  var CHAT_TIP = [
    'الذكاء الاصطناعي بيقرأ البرومبت بأول المحادثة. كل ما طوّلت المحادثة، بينسى قواعده: بيصير يعطيك الحل مباشرة، أو بيخلط بين المواد. محادثة جديدة يعني قواعد جديدة ومركّزة على موضوعك.',
    '✅ نفس المحادثة: مواضيع مرتبطة ببعض، أو امتحان تجريبي.',
    '🆕 محادثة جديدة: مادة تانية، أو موضوع جديد بيوم تاني، أو محادثة صارت طويلة كتير.'
  ];
  var ATTACH = '📎 الصق البرومبت، وبعدين اضغط + بالتطبيق، وارفق الصور (2 لـ 4 صور، كل صفحة بصورة، مستقيمة وبضو منيح)، وابعتهم مع بعض برسالة وحدة.';
  var NOTE_EXAMPLES = 'مثلاً: بحب الفيزيا، خلّي الأمثلة منها · ركّز على الغلطات بالإشارات · اشرح ببطء · امتحاني يوم الأحد';
  var MINISTRY = 'https://meyda.education.gov.il/';
  var TOTAL = 4;

  var data = null;
  var state = { step: 1, subject: null, grade: null, units: null, target: null, topics: {}, custom: [], modes: {}, teacherFile: false, remind: false, note: '', targetOpen: false, view: 'main' };
  var app = document.getElementById('app');
  var backButton = document.getElementById('back');
  var progress = document.getElementById('progress');
  var logLink = document.getElementById('log-link');
  var wide = window.matchMedia ? window.matchMedia('(min-width: 960px)') : { matches: false };
  var status = '';

  function h(tag, attrs) {
    var el = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (key) {
      var value = attrs[key];
      if (value === false || value == null) return;
      if (key === 'class') el.className = value;
      else if (key === 'text') el.textContent = value;
      else if (key.slice(0, 2) === 'on') el.addEventListener(key.slice(2), value);
      else el.setAttribute(key, value === true ? '' : value);
    });
    for (var i = 2; i < arguments.length; i++) {
      var child = arguments[i];
      if (child == null || child === false) continue;
      el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    }
    return el;
  }

  function subjectData() {
    return data.subjects.filter(function (s) { return s.id === state.subject; })[0] || null;
  }
  function gradeData() {
    var s = subjectData();
    return s ? s.grades.filter(function (g) { return g.id === state.grade; })[0] || null : null;
  }
  function levelData(units) {
    var g = gradeData();
    return g ? g.levels.filter(function (l) { return l.units === units; })[0] || null : null;
  }

  /* the ticked modes, in the order of the prompt (the plan first) */
  function pickedModes() {
    return P.PROMPT_ORDER.filter(function (m) { return state.modes[m]; });
  }

  function modeLabels() {
    return pickedModes().map(function (m) { return P.MODES[m].label; }).join(' + ');
  }

  function currentLevel() {
    return state.subject && state.grade && state.units ? { subject: state.subject, grade: state.grade, units: state.units } : null;
  }

  /* localStorage can be missing, blocked or full: it is only touched inside try/catch (here and in log.js) */
  function storage() {
    try { return window.localStorage; } catch (error) { return null; }
  }

  function levelLabel(level) {
    var subject = data.subjects.filter(function (s) { return s.id === level.subject; })[0];
    var grade = subject && subject.grades.filter(function (g) { return g.id === level.grade; })[0];
    return (subject ? subject.name : level.subject) + '، الصف ' + (grade ? grade.name : level.grade) + '، ' + level.units + ' وحدات';
  }

  function oldMistakes() {
    var level = currentLevel();
    var loaded = L.load(storage());
    return level && loaded.ok ? L.mistakesFor(loaded.entries, level) : [];
  }

  function selectedTopicIds() {
    return Object.keys(state.topics).filter(function (id) { return state.topics[id]; });
  }

  /* "all topics" means every topic of the student's own level; the target level's topics are ticked one by one */
  function allIds() {
    var level = state.units ? levelData(state.units) : null;
    return level ? level.topics.map(function (t) { return t.id; }) : [];
  }

  function checkedCustom() {
    return state.custom.filter(function (c) { return c.checked; }).map(function (c) { return c.text; });
  }

  function hasSelection() {
    return selectedTopicIds().length > 0 || checkedCustom().length > 0;
  }
  function isAll() {
    var ids = allIds();
    return ids.length > 0 && ids.every(function (id) { return state.topics[id]; });
  }

  function resetFrom() {
    /* the level changed: topics, mode and the later steps start again */
    state.target = null;
    state.step = 1;
    state.topics = {};
    state.modes = {};
  }

  function go(step) {
    state.step = step;
    status = '';
    render();
    if (!wide.matches) window.scrollTo(0, 0);
    app.focus({ preventScroll: true });
  }

  /* ---------------------------------------------------------------- step 1 */
  function choiceButton(label, pressed, onClick, badge) {
    return h('button', { type: 'button', class: 'choice', 'aria-pressed': pressed ? 'true' : 'false', onclick: onClick },
      label, badge ? h('span', { class: 'badge', text: badge }) : null);
  }

  function stepLevel() {
    var section = h('section', { class: 'step', 'data-step': '1' }, h('h1', { text: 'شو مستواك؟' }));

    section.appendChild(h('h2', { text: 'المادة' }));
    var subjects = h('div', { class: 'choices', role: 'group', 'aria-label': 'المادة' });
    data.subjects.forEach(function (s) {
      subjects.appendChild(choiceButton(s.name, state.subject === s.id, function () {
        if (state.subject !== s.id) { state.subject = s.id; state.grade = null; state.units = null; resetFrom(); }
        render();
      }));
    });
    section.appendChild(subjects);

    var subject = subjectData();
    if (subject) {
      section.appendChild(h('h2', { text: 'الصف' }));
      var grades = h('div', { class: 'choices', role: 'group', 'aria-label': 'الصف' });
      subject.grades.forEach(function (g) {
        grades.appendChild(choiceButton(g.name, state.grade === g.id, function () {
          if (state.grade !== g.id) { state.grade = g.id; state.units = null; resetFrom(); }
          render();
        }));
      });
      section.appendChild(grades);
    }

    var grade = gradeData();
    if (grade) {
      section.appendChild(h('h2', { text: 'الوحدات' }));
      var units = h('div', { class: 'choices', role: 'group', 'aria-label': 'الوحدات' });
      grade.levels.forEach(function (l) {
        units.appendChild(choiceButton(l.units + ' وحدات', state.units === l.units, function () {
          if (state.units !== l.units) { state.units = l.units; resetFrom(); }
          render();
        }, l.experimental ? 'تجريبي' : null));
      });
      section.appendChild(units);
    }

    var higher = grade ? grade.levels.filter(function (l) { return state.units && l.units > state.units; }) : [];
    if (higher.length) {
      section.appendChild(h('h2', { text: 'مستوى هدف (اختياري)' }));
      section.appendChild(h('p', { class: 'small', text: 'إذا بدك تنتقل لمستوى أعلى، اختاره وبنضيف مواضيعه.' }));
      var targets = h('div', { class: 'choices', role: 'group', 'aria-label': 'مستوى هدف' });
      targets.appendChild(choiceButton('بدون هدف', !state.target, function () { state.target = null; state.step = 1; state.topics = {}; render(); }));
      higher.forEach(function (l) {
        targets.appendChild(choiceButton(l.units + ' وحدات', state.target === l.units, function () {
          state.target = l.units; state.step = 1; state.topics = {}; render();
        }, l.experimental ? 'تجريبي' : null));
      });
      section.appendChild(targets);
    }

    if (state.step === 1) {
      var ready = !!(state.subject && state.grade && state.units);
      section.appendChild(h('div', { class: 'stack sticky' },
        h('button', { type: 'button', class: 'primary', id: 'next-1', disabled: !ready, onclick: function () { go(2); } }, 'التالي')));
    }
    return section;
  }

  /* ---------------------------------------------------------------- step 2 */
  function topicRow(topic) {
    var input = h('input', { type: 'checkbox', value: topic.id, 'data-topic': topic.id });
    input.checked = !!state.topics[topic.id];
    input.addEventListener('change', function () {
      state.topics[topic.id] = input.checked;
      if (state.step > 2) { render(); return; }
      document.getElementById('all-topics').setAttribute('aria-pressed', isAll() ? 'true' : 'false');
      document.getElementById('next-2').disabled = !hasSelection();
    });
    return h('label', { class: 'topic' }, input, h('span', { text: topic.title }));
  }

  /* topics the student writes himself: plain text, at most 5, each at most 60 characters */
  function customBox() {
    var limit = P.MAX_CUSTOM;
    var message = h('p', { class: 'small', id: 'custom-msg', role: 'status', 'aria-live': 'polite' });
    var input = h('input', { type: 'text', id: 'custom-input', maxlength: String(P.MAX_CUSTOM_LENGTH), autocomplete: 'off',
      'aria-label': 'ضيف موضوع مش موجود بالقائمة', placeholder: 'مثلاً: المعادلات التربيعية' });
    var add = h('button', { type: 'submit', id: 'custom-add' }, 'ضيف');
    if (state.custom.length >= limit) { input.disabled = true; add.disabled = true; message.textContent = 'وصلت للحد: ' + limit + ' مواضيع.'; }

    var form = h('form', { class: 'customform', onsubmit: function (event) {
      event.preventDefault();
      var text = P.cleanTopic(input.value);
      if (!text) { message.textContent = 'اكتب اسم الموضوع أول.'; return; }
      if (state.custom.some(function (c) { return c.text.toLowerCase() === text.toLowerCase(); })) { message.textContent = 'هالموضوع مضاف.'; return; }
      if (state.custom.length >= limit) return;
      state.custom.push({ text: text, checked: true });
      render();
      var again = document.getElementById('custom-input');
      if (again && !again.disabled) again.focus();
    } }, input, add);

    var list = h('ul', { class: 'customlist', id: 'custom-list' });
    state.custom.forEach(function (item, index) {
      var box = h('input', { type: 'checkbox', 'data-custom': String(index) });
      box.checked = item.checked;
      box.addEventListener('change', function () {
        item.checked = box.checked;
        if (state.step > 2) { render(); return; }
        document.getElementById('next-2').disabled = !hasSelection();
      });
      list.appendChild(h('li', { class: 'customitem' },
        h('label', { class: 'topic' }, box, h('span', { text: item.text })),
        h('button', { type: 'button', class: 'del', 'aria-label': 'احذف: ' + item.text, onclick: function () {
          state.custom.splice(index, 1);
          render();
          var again = document.getElementById('custom-input');
          if (again) again.focus();
        } }, 'حذف')));
    });

    return h('div', { class: 'custom' }, h('h2', { text: 'ضيف موضوع مش موجود بالقائمة' }), form, message, list);
  }

  function stepTopics() {
    var section = h('section', { class: 'step', 'data-step': '2' }, h('h1', { text: 'شو بدك تراجع؟' }));
    var levels = [levelData(state.units)];
    if (state.target) levels.push(levelData(state.target));

    section.appendChild(h('button', { type: 'button', class: 'alltopics', id: 'all-topics', 'aria-pressed': isAll() ? 'true' : 'false', onclick: function () {
      var next = !isAll();
      allIds().forEach(function (id) { state.topics[id] = next; });
      render();
    } }, 'كل المواضيع'));

    /* the box for a topic that is not on the list comes right under "all topics" */
    section.appendChild(customBox());

    levels.forEach(function (level, index) {
      if (!level) return;
      var lastGroup = null;
      var box = h('div', { class: 'group' });
      level.topics.forEach(function (topic) {
        if (topic.group && topic.group !== lastGroup) {
          box.appendChild(h('h2', { text: topic.group }));
          lastGroup = topic.group;
        }
        box.appendChild(topicRow(topic));
      });
      if (index === 0) { section.appendChild(box); return; }
      /* the topics of the target level are in a section that is closed until the student opens it */
      var target = h('details', { class: 'targetbox', id: 'target-topics' },
        h('summary', { text: 'مواضيع مستوى الهدف (' + level.units + ' وحدات)' }), box);
      if (state.targetOpen) target.open = true;
      target.addEventListener('toggle', function () { state.targetOpen = target.open; });
      section.appendChild(target);
    });

    if (state.step === 2) {
      var ready = hasSelection();
      section.appendChild(h('div', { class: 'stack sticky' },
        h('button', { type: 'button', class: 'primary', id: 'next-2', disabled: !ready, onclick: function () { go(3); } }, 'التالي')));
    }
    return section;
  }

  /* ---------------------------------------------------------------- step 3 */
  function stepMode() {
    var section = h('section', { class: 'step', 'data-step': '3' }, h('h1', { text: 'شو بدك تعمل؟' }));
    var subject = subjectData();
    section.appendChild(h('p', { class: 'hint', text: 'اختار وضع أو أكتر. بيبلّش بأول واحد وبينتقل للباقي.' }));
    P.MODE_ORDER.forEach(function (key) {
      /* practice and the mock exam are built on the exam patterns: a subject without them only gets explain and plan */
      if ((key === 'practice' || key === 'mock') && !(subject && subject.patterns)) return;
      /* a tap only ticks the mode: the options under the four cards (the teacher's file, the note) are still to be seen */
      var box = h('input', { type: 'checkbox', 'data-mode': key, id: 'mode-' + key });
      box.checked = !!state.modes[key];
      var card = h('label', { class: 'mode', 'data-mode': key, 'data-on': box.checked ? 'true' : 'false' }, box,
        h('span', { class: 'mode-text' }, h('strong', { class: 'mode-title', text: P.MODES[key].label }), h('span', { class: 'mode-note', text: P.MODES[key].description })));
      box.addEventListener('change', function () {
        state.modes[key] = box.checked;
        if (state.step > 3) { render(); return; }
        card.setAttribute('data-on', box.checked ? 'true' : 'false');
        document.getElementById('prepare').disabled = pickedModes().length === 0;
      });
      section.appendChild(card);
    });
    section.appendChild(extrasBox(subject));
    if (state.step === 3) {
      section.appendChild(h('div', { class: 'stack sticky' },
        h('button', { type: 'button', class: 'primary', id: 'prepare', disabled: pickedModes().length === 0, onclick: function () {
          L.rememberLevel(storage(), currentLevel());  // so that "سجلّي" knows the level after a reload
          go(4);
        } }, 'جهّز البرومبت')));
    }
    return section;
  }

  /* Under the four modes: a tick for an old exam or worksheet from the teacher (nothing is uploaded here: the
     student attaches the photos in his own app), and a note to the tutor of at most 200 characters. */
  function extrasBox(subject) {
    var box = h('div', { class: 'extras' });
    if (subject && subject.patterns) {
      var tick = h('input', { type: 'checkbox', id: 'teacher-file' });
      tick.checked = state.teacherFile;
      tick.addEventListener('change', function () { state.teacherFile = tick.checked; });
      box.appendChild(h('label', { class: 'topic' }, tick, h('span', null, 'عندي امتحان قديم أو ورقة عمل من أستاذي',
        h('small', { class: 'hint', text: 'بيشتغل مع "تدرّب" و"امتحان تجريبي" بس.' }))));
    }
    /* only when this student has saved entries for this very level */
    var level = currentLevel();
    var saved = level ? L.forLevel(L.load(storage()).entries, level) : [];
    if (saved.length) {
      var remind = h('input', { type: 'checkbox', id: 'remind' });
      remind.checked = state.remind;
      remind.addEventListener('change', function () { state.remind = remind.checked; });
      box.appendChild(h('label', { class: 'topic' }, remind, h('span', null, 'ذكّرني بغلطاتي القديمة',
        h('small', { class: 'hint', text: 'من ' + saved.length + ' جلسة محفوظة بسجلّي لهالمستوى.' }))));
    }
    var area = h('textarea', { id: 'note', maxlength: String(P.MAX_NOTE), rows: '3', 'aria-label': 'ملاحظة للمدرّس (اختياري)' });
    area.value = state.note;
    var count = h('span', { id: 'note-count', class: 'hint', text: area.value.length + ' / ' + P.MAX_NOTE });
    area.addEventListener('input', function () {
      state.note = area.value;
      count.textContent = area.value.length + ' / ' + P.MAX_NOTE;
    });
    var details = h('details', { class: 'notebox', id: 'note-box' }, h('summary', { text: 'ملاحظة للمدرّس (اختياري)' }), area,
      h('p', { class: 'hint', text: NOTE_EXAMPLES }), count);
    if (state.note) details.open = true;
    box.appendChild(details);
    return box;
  }

  /* ---------------------------------------------------------------- step 4 */
  function topicCount(n) {
    if (n === 1) return 'موضوع واحد';
    if (n === 2) return 'موضوعين';
    return n + (n <= 10 ? ' مواضيع' : ' موضوع');
  }

  function currentPrompt() {
    return P.buildPrompt(data, {
      subject: state.subject, grade: state.grade, units: state.units, target: state.target,
      all: isAll(), topics: selectedTopicIds(), custom: checkedCustom(), modes: pickedModes(),
      mistakes: state.remind ? oldMistakes() : [],
      teacherFile: state.teacherFile, note: state.note
    });
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return legacyCopy(text); });
    }
    return Promise.resolve(legacyCopy(text));
  }

  function legacyCopy(text) {
    var area = h('textarea', { 'aria-hidden': 'true', readonly: true, style: 'position:fixed;opacity:0;top:0;inset-inline-start:0' });
    area.value = text;
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(area);
    return ok;
  }

  function setStatus(text) {
    status = text;
    var el = document.getElementById('status');
    if (el) el.textContent = text;
  }

  var COPIED = 'انسخنا البرومبت، افتح التطبيق والصقه';

  function openInApp(text) {
    return copyText(text).then(function (copied) {
      if (navigator.share) {
        return navigator.share({ text: text }).then(function () {
          setStatus(copied ? 'تم. والبرومبت كمان منسوخ بالحافظة.' : 'تم.');
        }, function () {
          setStatus(copied ? COPIED : 'ما قدرنا ننسخ لحالنا: اضغط "انسخ" أو حدّد النص من "شوف البرومبت".');
        });
      }
      setStatus(copied ? COPIED : 'ما قدرنا ننسخ لحالنا: اضغط "انسخ" أو حدّد النص من "شوف البرومبت".');
    });
  }

  /* Android: a Chrome intent that opens the installed app and falls back to the site when it is not installed.
     Everywhere else: the plain https address. Only the official addresses, no private schemes. */
  function isAndroid() {
    return /android/i.test(navigator.userAgent || '');
  }

  /* iPhone, iPad and iPod. An iPad with "desktop" Safari says it is a Mac, but it has a touch screen. */
  function isIOS() {
    return /iPhone|iPad|iPod/.test(navigator.userAgent || '') || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  }

  function appAddress(app) {
    if (!isAndroid()) return app.url;
    return 'intent://' + app.host + '/' + app.path + '#Intent;scheme=https;package=' + app.package +
      ';S.browser_fallback_url=' + encodeURIComponent(app.url) + ';end';
  }

  /* iOS opens the installed app (a universal link) only when the student taps a normal link. So on iOS the click is not
     stopped and nothing is opened by the script: the link goes to the plain https address by itself, in the same tab.
     The copy has to start inside the click, before the page is left. */
  function copyInsideClick(text) {
    var failed = 'ما قدرنا ننسخ لحالنا: حدّد النص من "شوف البرومبت" وانسخه.';
    setStatus('انسخنا البرومبت. الصقه بالتطبيق.');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        navigator.clipboard.writeText(text).then(null, function () { if (!legacyCopy(text)) setStatus(failed); });
        return;
      } catch (error) { /* an old browser: the fallback below */ }
    }
    if (!legacyCopy(text)) setStatus(failed);
  }

  /* On Android and on a computer: the button of an app copies the prompt first, says so, and only then opens the app. */
  function openApp(app, text) {
    return copyText(text).then(function (copied) {
      setStatus(copied ? 'انسخنا البرومبت. الصقه بالتطبيق.' : 'ما قدرنا ننسخ لحالنا: حدّد النص من "شوف البرومبت" وانسخه.');
      var address = appAddress(app);
      if (isAndroid()) { window.open(address, '_self'); return; }
      var tab = window.open(address, '_blank');
      if (tab) { try { tab.opener = null; } catch (e) { /* cross-origin: nothing to do */ } } else window.location.href = address;
    });
  }

  function stepReady() {
    var built = currentPrompt();
    var section = h('section', { class: 'step', 'data-step': '4' }, h('h1', { text: 'جاهز' }));
    if (!built) { section.appendChild(h('p', { class: 'warn', text: 'ما لقينا هالمستوى. ارجع واختار من جديد.' })); return section; }

    var subject = subjectData();
    var grade = gradeData();
    var picked = selectedTopicIds().length;
    var own = allIds().length;
    var titles = picked ? topicCount(picked) : '';
    if (isAll()) titles = 'كل المواضيع' + (picked > own ? ' + ' + topicCount(picked - own) + ' من الهدف' : '');
    if (checkedCustom().length) titles += (titles ? ' + ' : '') + checkedCustom().length + ' من عندك';
    section.appendChild(h('div', { class: 'summary', id: 'summary' },
      h('p', { text: subject.name + '، الصف ' + grade.name + '، ' + state.units + ' وحدات' + (state.target ? ' (هدف: ' + state.target + ' وحدات)' : '') }),
      h('p', { id: 'summary-modes', text: titles + ' • ' + modeLabels() }),
      h('p', { id: 'length', text: 'طول البرومبت: ' + built.length + ' حرف' })));

    if (built.tooLong) {
      section.appendChild(h('p', { class: 'warn', id: 'too-long', role: 'alert',
        text: 'اخترت مواضيع كتير والبرومبت طويل (' + built.length + ' حرف، الحد ' + built.max + '). التطبيقات بتتعامل أحسن مع برومبت أقصر: ارجع واختار مواضيع أقل.' }));
    }
    var level = levelData(state.units);
    if (level && level.experimental) {
      section.appendChild(h('p', { class: 'warn', id: 'experimental', text: 'هالمستوى تجريبي: لسا ما إلو أمثلة جاهزة على نمط الامتحان.' }));
    }

    if (built.teacherFile) section.appendChild(h('p', { class: 'attach', id: 'attach', text: ATTACH }));

    section.appendChild(h('div', { class: 'stack' },
      h('button', { type: 'button', class: 'primary', id: 'open-app', onclick: function () { openInApp(built.text); } }, 'افتح بتطبيق الذكاء الاصطناعي'),
      h('p', { class: 'hint', id: 'open-hint', text: 'الأحسن: بيحط البرومبت جوا التطبيق مباشرة.' }),
      h('button', { type: 'button', id: 'copy', onclick: function () {
        copyText(built.text).then(function (ok) { setStatus(ok ? 'تم النسخ.' : 'ما قدرنا ننسخ لحالنا: حدّد النص من "شوف البرومبت".'); });
      } }, 'انسخ')));
    section.appendChild(h('p', { class: 'status', id: 'status', role: 'status', 'aria-live': 'polite', text: status }));

    section.appendChild(h('h2', { text: 'أو افتح التطبيق بنفسك والصق' }));
    var apps = h('div', { class: 'apps' });
    APPS.forEach(function (a) {
      var ios = isIOS();
      apps.appendChild(h('a', { class: 'linkbtn', href: appAddress(a), target: ios ? null : '_blank', rel: 'noopener noreferrer', 'data-app': a.name,
        onclick: ios ? function () { copyInsideClick(built.text); } : function (event) { event.preventDefault(); openApp(a, built.text); } }, a.name));
    });
    section.appendChild(apps);

    section.appendChild(h('p', { class: 'note', style: 'margin-top:16px', text: 'صوّر حلّك على الورقة وابعته بالتطبيق.' }));
    section.appendChild(h('p', { class: 'note' }, 'بدك تتدرّب على امتحان كامل؟ نزّله وارفعه للأداة. ',
      h('a', { href: MINISTRY, target: '_blank', rel: 'noopener noreferrer', id: 'exams-link', text: 'امتحانات رسمية سابقة' })));

    section.appendChild(h('details', { id: 'chat-tip' }, h('summary', { text: '💡 ليش كل مادة أو موضوع جديد بمحادثة جديدة؟' }),
      h('div', { class: 'tip' }, h('p', { text: CHAT_TIP[0] }), h('p', { text: CHAT_TIP[1] }), h('p', { text: CHAT_TIP[2] }))));

    var preview = h('pre', { id: 'preview', text: built.text });
    section.appendChild(h('details', null, h('summary', { text: 'شوف البرومبت' }), preview));
    return section;
  }

  /* ---------------------------------------------------------------- سجلّي */
  var logMessage = '';
  var logDraft = '';

  function logPage() {
    var loaded = L.load(storage());
    var level = currentLevel() || L.lastLevel(storage());
    var section = h('section', { class: 'step', id: 'log-page', 'data-step': 'log' }, h('h1', { text: 'سجلّي' }),
      /* why the log, and how: short, right under the title, before the privacy line */
      h('div', { class: 'summary', id: 'log-why' },
        h('strong', { text: 'ليش سجلّي؟ (اختياري، بس مفضّل)' }),
        h('p', { text: 'المحادثة الجديدة ما بتتذكّر غلطاتك. سجلّي بيحفظها، وبيخلّي المدرّس يفحصك عليها بالمرة الجاية.' }),
        h('strong', { text: 'كيف؟' }),
        h('ol', null,
          h('li', { text: 'بآخر الجلسة اكتب للمدرّس: خلصت' }),
          h('li', { text: 'انسخ الملخص اللي بيبلّش بـ NMI-LOG' }),
          h('li', { text: 'الصقه هون واضغط احفظ' }),
          h('li', { text: 'بالمرة الجاية علّم «ذكّرني بغلطاتي القديمة»' }))),
      h('p', { class: 'hint', id: 'log-privacy', text: 'السجل محفوظ على هاد الجهاز بس. ما بيوصلنا ولا إشي.' }));
    if (!loaded.ok) section.appendChild(h('p', { class: 'warn', id: 'log-unavailable', role: 'alert', text: L.NO_STORAGE }));

    section.appendChild(h('p', { class: 'note', id: 'log-level', text: level ? 'المستوى: ' + levelLabel(level) : 'لسا ما اخترت مستواك: ابنِ برومبت من الصفحة الرئيسية وبعدين ارجع.' }));
    var area = h('textarea', { id: 'log-input', rows: '6', 'aria-label': 'الصق ملخّص الجلسة' });
    area.value = logDraft;
    area.addEventListener('input', function () { logDraft = area.value; });
    section.appendChild(h('label', { for: 'log-input', class: 'logtitle', text: 'الصق ملخّص الجلسة' }));
    section.appendChild(area);
    section.appendChild(h('div', { class: 'stack' }, h('button', { type: 'button', class: 'primary', id: 'log-save', onclick: function () {
      var result = L.add(storage(), area.value, level, new Date());
      if (result.ok) { logDraft = ''; logMessage = 'انحفظ.'; } else logMessage = result.message;
      render();
    } }, 'احفظ')));
    section.appendChild(h('p', { class: 'status', id: 'log-msg', role: 'status', 'aria-live': 'polite', text: logMessage }));

    if (loaded.entries.length) {
      var list = h('ul', { class: 'loglist', id: 'log-list' });
      loaded.entries.forEach(function (entry) {
        list.appendChild(h('li', { class: 'logitem', 'data-id': entry.id },
          h('p', { class: 'logmeta', text: entry.date.slice(0, 10) + ' • ' + levelLabel(entry) }),
          h('pre', { class: 'logtext', text: entry.text }),
          h('button', { type: 'button', class: 'del', 'aria-label': 'امسح هالمدخل', onclick: function () {
            var result = L.remove(storage(), entry.id);
            logMessage = result.ok ? '' : result.message;
            render();
          } }, 'امسح')));
      });
      section.appendChild(h('h2', { text: 'الجلسات المحفوظة' }));
      section.appendChild(list);
      section.appendChild(h('div', { class: 'stack' }, h('button', { type: 'button', id: 'log-clear', onclick: function () {
        var result = L.clear(storage());
        logMessage = result.ok ? '' : result.message;
        render();
      } }, 'امسح الكل')));
    }
    section.appendChild(h('div', { class: 'stack' }, h('button', { type: 'button', id: 'log-close', onclick: function () { state.view = 'main'; render(); } }, 'رجوع للعدّة')));
    return section;
  }

  /* ---------------------------------------------------------------- page */
  function render() {
    logLink.setAttribute('aria-pressed', state.view === 'log' ? 'true' : 'false');
    if (state.view === 'log') {
      app.textContent = '';
      app.appendChild(logPage());
      backButton.hidden = true;
      progress.textContent = '';
      document.body.setAttribute('data-step', 'log');
      return;
    }
    var steps = [stepLevel, stepTopics, stepMode, stepReady];
    var visible = wide.matches ? steps.slice(0, state.step) : [steps[state.step - 1]];
    app.textContent = '';
    visible.forEach(function (build, index) {
      var section = build();
      if (wide.matches && index < state.step - 1) section.setAttribute('data-done', '');
      app.appendChild(section);
    });
    backButton.hidden = state.step === 1;
    progress.textContent = 'الخطوة ' + state.step + ' من ' + TOTAL;
    document.body.setAttribute('data-step', String(state.step));
  }

  logLink.addEventListener('click', function () {
    if (!data) return;
    state.view = state.view === 'log' ? 'main' : 'log';
    render();
    if (!wide.matches) window.scrollTo(0, 0);
  });
  backButton.addEventListener('click', function () { if (state.step > 1) go(state.step - 1); });
  if (wide.addEventListener) wide.addEventListener('change', render);

  fetch('data.json').then(function (response) {
    if (!response.ok) throw new Error('data');
    return response.json();
  }).then(function (json) {
    data = json;
    if (data.subjects.length === 1) state.subject = data.subjects[0].id;
    render();
  }).catch(function () {
    app.textContent = '';
    app.appendChild(h('p', { class: 'warn', role: 'alert', text: 'ما قدرنا نحمّل المنهاج. افتح الصفحة من الرابط الرسمي وحدّث.' }));
  });
}());
