# NMI chat-first preview verification

Historical 12 October report. For the current country/subject scope, approved ribbon identity and latest test results, see [13 October refinements](FRONTEND_REFINEMENTS.md). The free-text country and old logo descriptions below describe the earlier version.

12 October 2026. Product authority: [NMI_PRODUCT_SPEC.md](../NMI_PRODUCT_SPEC.md). Design approval and real backend integration are separate future steps.

## What changed

The previous lesson-centered specimen has been replaced by a conversation workspace: original NMI mark, quiet conversation sidebar, centered welcome, persistent bottom composer, search, history and secondary Progress/Curriculum/Library/Profile/Settings screens. Both languages and themes share central tokens. Native MathML, code blocks, copy, hints and short checks demonstrate conversation presentation with fixed replies.

First-time onboarding asks for language, a demo nickname, country and Grade 9, 10, 11 or 12 only. A configurable supported-grade list also validates restored state. An optional original illustrated avatar, subject interests, honest empty progress/strength/weakness states, demo history and Continue Learning appear in Profile. A separately labeled fictional progress specimen demonstrates subject/skill presentation and prerequisite recovery; it is never saved as an assessment. The exact avatar reference has not been supplied.

Browser-local synthetic profile and chats survive restart. Preferences use separate namespaced keys. Version/type/enum/length checks, bounded storage, safe text rendering, explicit reset, corruption preservation and stale-tab write detection protect the demo state. These are prototype safeguards, not authentication or multi-student isolation. Only sample details belong in this preview.

## Files changed in this redesign

| File | Change |
|---|---|
| NMI_PRODUCT_SPEC.md | New requirements authority, measurable acceptance criteria and future integration gate. |
| AGENTS.md | Product-spec authority, Grades 9-12 boundary and permitted synthetic persistence. |
| DESIGN.md | Replaced lesson direction with conversation layout, tokens, onboarding, privacy and research decisions. |
| preview/index.html | New sidebar, chat, utility screens, profile, onboarding and original inline avatar/icons. |
| preview/tokens.css | Shared restrained light/dark palette, type, spacing and motion roles. |
| preview/styles.css | Desktop chat composition, controls, logical RTL spacing, focus, motion and magnification support. |
| preview/preview.js | Two-language copy, mock interactions, onboarding, profile, search and validated demo persistence. |
| tests/frontend/preview.spec.cjs | Replaced lesson tests with chat/theme/locale/navigation/accessibility matrix. |
| tests/frontend/onboarding.spec.cjs | New onboarding, storage faults, stale-tab and browser-process restart tests. |
| tests/frontend/zoom.spec.cjs | New 2x CSS layout-magnification keyboard checks and lower-screen captures. |
| tests/frontend-state.test.cjs | New offline translation, grade and stored-state validation tests. |
| tests/evals/tutor_cases.json | Expanded from 14 to 22 cases with provenance, grade and unevaluated status. |
| tests/evals/README.md | Semantic rubrics, evidence requirements and separation from mock testing. |
| tools/validate_setup.py | Validate new evaluation metadata and require evidence for future pass/fail claims. |
| docs/SKILLS_SETUP.md; docs/TEST_RESULTS.md | Mark older lesson-preview results historical and link this report. |
| docs/PREVIEW_VERIFICATION.md | This handover and evidence record. |

The existing SVG logo, Python learning modules, teaching rules, curriculum text, requirements and student files were not changed. No new package, Skill, MCP server, framework or subscription was installed during this redesign. Artifacts and fresh test-browser profiles are under .cache, ignored by Git. The prior installed tools were reused.

## Skills actually read and applied

All twelve project Skill entrypoints were read. Referenced Motion best practices, Playwright testing/request-mocking/storage guidance, security acceptance cases and tutor evaluation guidance were also read. Installed Skill metadata and links pass validation.

| Skill | Concrete contribution | Evidence |
|---|---|---|
| frontend-design | Deliberate chat-first hierarchy, typography, original identity and restrained composition. | Welcome/chat/profile screenshot review. |
| nmi-design-system | One token source and shared controls across routes/themes. | Both-theme matrix and visual inspection. |
| nmi-bilingual-ui | Matching ar/en dictionaries, atomic lang/dir updates, bdi and LTR math/code. | Dictionary checks and bilingual UI tests. |
| nmi-frontend-quality | Desktop matrix, keyboard, storage faults, screenshots and truthful reporting. | Browser suites and recorded limitations. |
| web-design-guidelines | Native labels/dialogs, visible focus, validation, status regions and safe form behavior. | Static review plus axe A/AA checks; transient text-contrast defect fixed. |
| playwright-cli | Local Playwright test mechanics, isolated browser profiles, request blocking and restart verification. | Local @playwright/test runner; no global CLI or personal profile attached. |
| motion | Short transform feedback, no decorative animation, reduced-motion handling, CSS chosen for simple effects. | Reduced-motion test; no Motion MCP, MotionScore or paid tooling used. |
| nmi-tutor-testing | Intent versus assessment separation and expanded semantic evaluation rubrics. | 22 valid but semantically unevaluated cases; mocked contract tests reported separately. |
| nmi-backend-quality | Preserved module contracts and separated static preview from the client-initializing Python core. | Original 11-file hash baseline unchanged; integration gaps documented. |
| nmi-security-privacy | Safe rendering, bounded input, demo-only storage and future cookie/authorization requirements. | Literal HTML test, state validation, static-server deny tests; no real auth claim. |
| nmi-curriculum-quality | Verified-source requirement, no invented curriculum, stable prerequisite/grade contracts. | Empty curriculum UI, preserved fallback contract and evaluation cases. |
| nmi-reliability-testing | Preserve invalid data, surface storage failures, avoid stale overwrites, expose backend gaps. | Browser storage fault tests and isolated mocked backend suite. |

## Research applied

Read the public resources on 12 October 2026:

- [ChatGPT](https://chatgpt.com/): direct chat entry and new/search/history hierarchy; NMI keeps its own logo, wording, teal palette and identity.
- [21st.dev](https://21st.dev/): considered chat/navigation/component patterns; its React/Tailwind approach was not imported into the vanilla project. No component source or proprietary asset copied.
- [Supahero](https://supahero.io/): informed first-screen hierarchy and spacing rather than introducing a marketing hero into chat.
- [Refero Styles](https://styles.refero.design/): informed explicit palette, typography, spacing and component roles in DESIGN.md; no wholesale theme import.
- [Motion](https://motion.dev/): purposeful feedback with simple CSS and reduced-motion support. No runtime dependency required.
- [Vercel interface guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md): checked forms, focus, accessible labels, motion and bilingual formatting.

## Test results

- Main Playwright/Edge suite: **34 passed**, including full Arabic/English x light/dark x 1280x800, 1440x900, 1920x1080 welcome/chat matrix; onboarding in four locale/theme combinations; all sidebar screens; search; math/code; hints/checks; drafts; stop; long input; IME; safe literal text; reduced motion; and preview-server file restrictions.
- Storage tests: actual close/relaunch of a fresh persistent Edge profile restored onboarding, locale, theme and chat content. Corrupt, unsupported-version, unsupported-grade, oversized, blocked/full storage and another tab's changes were exercised. No personal browser profile was used.
- Magnification: two additional Arabic/English keyboard tests passed at 2x CSS layout zoom. Visual review then prompted a smaller minimum layout width; the affected matrix is rerun separately below. CSS zoom is not a native browser-toolbar zoom or screen-reader certification.
- Node state suite: **4 passed**, covering dictionary/key parity, grade boundaries, malformed state and allowlisted reconstruction.
- Skills/setup validator: **12 Skills passed**, **22 evaluation fixtures valid**, and **11 original backend/text/requirements file hashes unchanged**.
- Existing backend contract suite: **11 passed, 4 expected failures, 2 skipped**, using mocked OpenAI, network-denial guards and temporary paths. Expected failures identify current corrupt/wrong-shaped JSON handling, uncaught timeout and non-atomic progress/history writes. Skips identify absent Flask/student isolation and retry idempotency. These are not passed protections.
- Real tutor semantic evaluation: **not run**. The literal command "شوي" is user-supplied; other case messages/contexts are synthetic and labeled. No model training/improvement claim, real model inference or paid API request.

Final affected magnification/desktop/navigation rerun: **10 passed** (four 1280px locale/theme checks, four navigation/accessibility checks at 1440px, and the two 2x magnification checks). Across the main and additional suites, **36 distinct browser tests passed**. The final CSS change affected minimum-width behavior and profile wrapping; the affected checks were rerun after that change.

Automated axe checks reported no violations in the tested welcome, conversation, onboarding, profile, progress, fictional specimen, curriculum, library, settings, search and code states after fixes. This is limited to tested rules/states in Edge. Manual assistive-technology testing, native browser-toolbar zoom and other browser engines remain future checks.

Visual inspection covered actual screenshots of Arabic light welcome/chat, English dark welcome/profile, English light conversation, Arabic dark code, both onboarding languages/themes, profile lower content and prerequisite recovery. The avatar hide bug was fixed with an SVG attribute, text opacity animation was removed to preserve contrast, and magnification clipping was reduced without mobile navigation. Tall utility content scrolls within the workspace.

Raw results: .cache/frontend-main-results.json contains the 34-test run. .cache/frontend-results.json contains the most recent targeted run. Screenshots and synthetic test-browser profiles stay local. Initial automatic-review usage-limit failure was resolved when the new test launch was approved; only the verified earlier NMI preview process was stopped to free the test port.

## Screenshots

- [Arabic light welcome](../.cache/screenshots/chat-first-ar-light-1280-welcome.png)
- [English dark welcome](../.cache/screenshots/chat-first-en-dark-1440-welcome.png)
- [Arabic onboarding](../.cache/screenshots/onboarding-ar-light.png)
- [English dark onboarding](../.cache/screenshots/onboarding-en-dark.png)
- [English dark profile](../.cache/screenshots/chat-first-en-dark-profile.png)
- [Profile history and Continue Learning](../.cache/screenshots/profile-lower-en.png)
- [Arabic dark code conversation](../.cache/screenshots/chat-first-ar-dark-code.png)
- [English light mathematics](../.cache/screenshots/chat-first-en-light-1440-chat.png)
- [Earlier foundation and return to the original topic](../.cache/screenshots/prerequisite-recovery-ar.png)

## Open locally

From NMI:

```powershell
.\.venv\Scripts\python.exe -B tools/serve_preview.py
```

Open http://127.0.0.1:8765/ in a desktop browser. Keep the same origin/port to restore its saved demo. Complete onboarding with a nickname/sample details, try a prompt, switch language/theme, explore Profile and Progress, and close/reopen the browser. Settings can explicitly reset only the preview's saved data. This server serves allowlisted static files and never imports the tutor.

At handover the loopback preview server was started in a hidden window for local review. If it has stopped, use the command above. The final design is ready for the user's review; backend connection remains unapproved and disabled.

Recheck:

```powershell
node --test tests/frontend-state.test.cjs
node tools/run_frontend_tests.cjs
.\.venv\Scripts\python.exe -B tools/validate_setup.py
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/offline -v
```

## Remaining implementation boundaries

This is a working design prototype with canned responses, not adaptive AI. No real progress is assessed; fictional bars are labeled and fixed. Curriculum has no verified coverage loaded. Country input is free text for the local demo; future curriculum mapping needs validated jurisdiction IDs. Real semantic evaluation remains unevaluated.

Grades 9-12 are enforced in the preview; the preserved Python CLI still accepts an unrestricted grade string. Future backend enforcement must be implemented before integration. The backend still uses singleton JSON files and lacks secure multi-student repositories, transactions, robust failure handling and idempotency. No authentication, Remember Me session, Logout/revocation or deployment is claimed. Their requirements are documented in the product specification.

Demo localStorage is visible to anyone sharing the same browser profile. It is not an access-control boundary and must never contain real student data or credentials. Drafts are kept in the current tab and guarded on unload; completed demo conversations persist. Storage quotas may prevent saving, with a visible message. No live connection to AI or student records will be made before design approval and a separate safe integration task.

No parent duplicates, real student data or credentials were modified/accessed. No commit, push, public deployment or purchase was performed.
