# NMI setup verification — 2026-10-12

Historical results for the earlier lesson preview. See [PREVIEW_VERIFICATION.md](PREVIEW_VERIFICATION.md) for the current chat-first preview, onboarding, persistence and expanded evaluation dataset. Do not apply the older frontend pass count to the redesign.

## Skills and boundaries

- 12 unique Skills pass the bundled official quick_validate.py validator.
- All entrypoint relative reference links resolve inside NMI.
- 14 synthetic tutor evaluation cases pass format, ID uniqueness, language and non-attempt intent checks.
- SHA-256 checks confirm all 11 original top-level Python/text/requirements files match the pre-setup baseline. Git diff also confirms no existing NMI tracked file was modified.
- Git index remains empty. Parent duplicate changes and existing untracked parent files remain outside this task.
- Local .cache and node_modules are ignored by Git. No new files were staged or committed.
- Secret-pattern scan of project files (excluding environments/dependency/cache directories) found no API-key/private-key patterns. No credential files or credential values were accessed to perform this check.
- Discovery is structurally correct under NMI/.agents/skills. A fresh Codex session rooted in NMI is still needed to observe the selector and implicit invocation. The current parent-rooted session does not automatically scan child Skills.

## Browser tests

Command: `node tools/run_frontend_tests.cjs --max-failures=1`

Final result: **16 passed**, 38.9 seconds, Microsoft Edge with Chromium sandbox enabled. Each browser uses a fresh profile in NMI/.cache/browser-tmp. The test server serves only five allowed preview assets on 127.0.0.1, and the main matrix blocks external requests.

Twelve matrix tests cover Arabic/English × light/dark × 1280×800, 1440×900, 1920×1080. Each checks lang/dir/theme, LTR formula islands, no horizontal overflow at the supported width, accessible initial learning screen, navigation, blank input, safe rendering of HTML-like input, draft preservation across language switching, a synthetic reply/hint, theme switching, no unexpected localStorage keys, and no console/page errors.

Four additional tests cover preference persistence with conversation reset on reload, blocked localStorage and reduced motion, denial of backend/secret/traversal paths, and keyboard controls with skip-link preservation of the active view.

Automated axe checks found **zero violations of the selected WCAG A/AA rule tags on the initial learning screen in the 12 matrix states**. This is not a complete accessibility certification. Other browser engines, manual screen-reader operation and zoom/reflow review are not verified yet.

Screenshots were generated for all 12 matrix states. Arabic/light at 1280 and English/dark at 1440 were visually inspected. The Arabic inspection exposed reversed start/finish diagram semantics; direction and arrow mirroring were corrected and the full suite rerun. A skip link that reset the active page was also corrected and covered by a new keyboard regression test. No backend changes were involved.

The first browser run timed out during page creation in the execution sandbox. It was stopped; the same suite ran successfully with permission to launch a browser process. Browser security was not disabled. Tests complete and stop their local web server; no public service was started.

## Offline backend contracts

Command: `.venv/Scripts/python.exe -B -m unittest discover -s tests/offline -v`

Result: **17 tests: 11 passed, 4 expected failures, 2 skipped**. All use an in-process fake OpenAI module, denied socket connections and isolated synthetic files under NMI/.cache/offline. No real student storage is used.

Passed:

1. Missing student/history/progress defaults.
2. New student onboarding and mocked reply.
3. Returning profile remains byte-identical.
4. Normal question does not change progress.
5. Correct attempt saves and produces expected mastery.
6. Incorrect attempt preserves a supplied mistake type.
7. Missing parsed output preserves previous history/progress in Arabic and English.
8. Invalid assessment fields preserve history/progress (10 subcases).
9. Unicode chat/progress save-load round trips.
10. Missing country/grade curriculum fallback.
11. Matching synthetic curriculum marker lookup.

Expected failures demonstrate existing defects, not successful protection:

| Gap | Observed behavior |
|---|---|
| Corrupted JSON | Reading malformed progress raises JSONDecodeError rather than a controlled failure |
| Wrong stored shape | A JSON list is accepted by load_progress without schema validation |
| API timeout | A mocked TimeoutError escapes ask_ai rather than returning a friendly result |
| Partial write | Saving progress succeeds before history fails, so the two records diverge |

Skipped future contracts:

- Flask authorization and student isolation: no Flask app/authenticated repository exists.
- Retry deduplication: no request-ID/idempotency contract exists; identical answer text alone is not a safe duplicate detector.

These gaps were documented and left unchanged because the task prohibits changing NMI learning logic. Future implementation work should replace expected-failure/skip markers with positive tests as contracts become available.

## Semantic teaching evaluation

The 14 cases cover Arabic spelling mistakes, ambiguity, normal questions, hint progression, confusion, correct/incorrect answers, missing curriculum, adaptation and learner isolation. They are **prepared but semantically unevaluated**. Fixed mock responses prove validation/persistence plumbing, not that an AI model understands a typo or teaches effectively. No model-generated responses or paid API evaluation were requested.
