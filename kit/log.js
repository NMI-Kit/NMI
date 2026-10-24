/* "سجلّي": the mistakes log of the student. The session is inside ChatGPT, Claude or Gemini, so the kit cannot see
   the mistakes: the AI writes a short summary that starts with NMI-LOG, the student pastes it here, and the next
   prompt can remind the tutor of the old mistakes. Everything stays in the localStorage of this browser.
   Pure functions plus a thin storage wrapper: no DOM, no network. Every storage access is inside try/catch. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NMILog = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const START = 'NMI-LOG';
  const KEY = 'nmi-log-v1';
  const LEVEL_KEY = 'nmi-last-level-v1';
  const MAX_ENTRY = 600;     // characters per entry
  const MAX_ENTRIES = 20;    // the oldest is dropped
  const MISTAKES_ENTRIES = 3;
  const MISTAKES_CHARS = 600;
  const MISTAKE_PREFIX = 'غلط:';
  const NEWLINE = String.fromCharCode(10);

  const NOT_A_SUMMARY = 'هاد مش ملخص من المدرّس. انسخ الملخص اللي بيبلّش بـ NMI-LOG.';
  const NO_STORAGE = 'هالمتصفح ما بيقدر يحفظ. السجل ما رح ينحفظ.';

  /* control characters and invisible direction marks, except the line break */
  const HIDDEN = /[\u0000-\u0009\u000b-\u001f\u007f-\u009f‎-‏‪-‮⁦-⁩]/g;

  /* A code block that was copied together with its fence is still the summary. */
  function withoutFence(text) {
    return text.replace(/^```[^\n]*\n?/, '').replace(/\n?```\s*$/, '');
  }

  /* The text of an entry: plain text only. No HTML tags, no "==" at the start of a line (it would open a section of
     a prompt), no control characters, at most 600 characters. */
  function cleanText(text) {
    return String(text == null ? '' : text)
      .replace(/\r\n?/g, '\n')
      .replace(HIDDEN, ' ')
      .replace(/<[^>]*>/g, '')
      .split('\n').map(function (line) { return line.replace(/^[\s=]+/, '').replace(/[ \t]+$/, ''); }).join('\n')
      .replace(/\n{3,}/g, '\n\n').trim().slice(0, MAX_ENTRY).trim();
  }

  /* { ok: true, text } for a summary that starts with NMI-LOG (after trimming), { ok: false, message } otherwise. */
  function parseSummary(raw) {
    const trimmed = withoutFence(String(raw == null ? '' : raw).trim()).trim();
    if (trimmed.slice(0, START.length) !== START) return { ok: false, message: NOT_A_SUMMARY };
    const text = cleanText(trimmed);
    if (text.slice(0, START.length) !== START) return { ok: false, message: NOT_A_SUMMARY };
    return { ok: true, text: text };
  }

  function sameLevel(entry, level) {
    return !!level && entry.subject === level.subject && Number(entry.grade) === Number(level.grade) && Number(entry.units) === Number(level.units);
  }

  /* ---- storage: every call is guarded, a browser that cannot store gives { ok: false } and nothing else breaks */
  function read(storage) {
    try {
      if (!storage) return { ok: false, entries: [] };
      const raw = storage.getItem(KEY);
      if (!raw) return { ok: true, entries: [] };
      const list = JSON.parse(raw);
      if (!Array.isArray(list)) return { ok: true, entries: [] };
      const entries = list.filter(function (e) {
        return e && typeof e.text === 'string' && typeof e.date === 'string' && typeof e.id === 'string';
      }).map(function (e) {
        return { id: e.id, date: e.date, subject: String(e.subject), grade: Number(e.grade), units: Number(e.units), text: cleanText(e.text) };
      });
      return { ok: true, entries: entries.slice(0, MAX_ENTRIES) };
    } catch (error) {
      return { ok: false, entries: [] };
    }
  }

  function write(storage, entries) {
    try {
      if (!storage) return false;
      storage.setItem(KEY, JSON.stringify(entries.slice(0, MAX_ENTRIES)));
      return true;
    } catch (error) {
      return false;
    }
  }

  /* Newest first. Returns { ok, entries, message? }. */
  function load(storage) {
    const result = read(storage);
    return result.ok ? result : { ok: false, entries: [], message: NO_STORAGE };
  }

  /* level: { subject, grade, units }. now: a Date. */
  function add(storage, raw, level, now) {
    const parsed = parseSummary(raw);
    if (!parsed.ok) return { ok: false, entries: load(storage).entries, message: parsed.message };
    if (!level || !level.subject || !level.grade || !level.units) {
      return { ok: false, entries: load(storage).entries, message: 'اختار مستواك أول: ابنِ برومبت من الصفحة الرئيسية وبعدين ارجع.' };
    }
    const current = read(storage);
    const when = now instanceof Date ? now : new Date();
    const entry = {
      id: when.getTime() + '-' + Math.random().toString(36).slice(2, 7), date: when.toISOString(),
      subject: String(level.subject), grade: Number(level.grade), units: Number(level.units), text: parsed.text
    };
    const entries = [entry].concat(current.entries).slice(0, MAX_ENTRIES);
    if (!write(storage, entries)) return { ok: false, entries: current.entries, message: NO_STORAGE };
    return { ok: true, entries: entries, entry: entry };
  }

  function remove(storage, id) {
    const current = read(storage);
    const entries = current.entries.filter(function (e) { return e.id !== id; });
    if (!write(storage, entries)) return { ok: false, entries: current.entries, message: NO_STORAGE };
    return { ok: true, entries: entries };
  }

  function clear(storage) {
    try {
      if (!storage) return { ok: false, entries: [], message: NO_STORAGE };
      storage.removeItem(KEY);
      return { ok: true, entries: [] };
    } catch (error) {
      return { ok: false, entries: read(storage).entries, message: NO_STORAGE };
    }
  }

  /* The level of the last prompt the student built, so that "سجلّي" knows it after the page was reloaded. */
  function rememberLevel(storage, level) {
    try {
      if (storage && level && level.subject && level.grade && level.units) {
        storage.setItem(LEVEL_KEY, JSON.stringify({ subject: String(level.subject), grade: Number(level.grade), units: Number(level.units) }));
      }
    } catch (error) { /* a browser that cannot store: the log asks for the level instead */ }
  }

  function lastLevel(storage) {
    try {
      const value = JSON.parse(storage.getItem(LEVEL_KEY));
      return value && value.subject && value.grade && value.units ? { subject: String(value.subject), grade: Number(value.grade), units: Number(value.units) } : null;
    } catch (error) {
      return null;
    }
  }

  function forLevel(entries, level) {
    return entries.filter(function (e) { return sameLevel(e, level); });
  }

  /* The "غلط:" lines of the last 3 entries of this level (newest first), at most 600 characters together. */
  function mistakesFor(entries, level) {
    const lines = [];
    const chosen = forLevel(entries, level).slice(0, MISTAKES_ENTRIES);
    chosen.forEach(function (entry) {
      entry.text.split(/\n/).forEach(function (line) {
        const trimmed = line.trim();
        if (trimmed.slice(0, MISTAKE_PREFIX.length) !== MISTAKE_PREFIX) return;
        const room = MISTAKES_CHARS - (lines.length ? lines.join(NEWLINE).length + 1 : 0);  // + the line break before this line
        if (room < 12) return;
        lines.push(trimmed.slice(0, room).trim());
      });
    });
    return lines;
  }

  return {
    START: START, KEY: KEY, MAX_ENTRY: MAX_ENTRY, MAX_ENTRIES: MAX_ENTRIES, MISTAKES_CHARS: MISTAKES_CHARS,
    NOT_A_SUMMARY: NOT_A_SUMMARY, NO_STORAGE: NO_STORAGE,
    parseSummary: parseSummary, cleanText: cleanText, load: load, add: add, remove: remove, clear: clear,
    forLevel: forLevel, mistakesFor: mistakesFor, rememberLevel: rememberLevel, lastLevel: lastLevel
  };
});
