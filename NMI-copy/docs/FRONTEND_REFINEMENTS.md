# NMI frontend refinements — 13 October 2026

The static desktop preview retains its chat-first layout, all sidebar destinations, onboarding, returning demo profiles, chat history, themes, math/code formatting, hints and comprehension prompts. Python tutoring modules remain unchanged. No real AI integration, student records, authentication or deployment was added.

## Product scope implemented

- Any topic may be sent and preserved as a demo conversation. Replies are fixed samples; this does not implement real general-topic tutoring.
- Only Mathematics, Physics and Chemistry appear as academic choices and in Progress/Curriculum summaries. Other conversations have no academic learning-path bar or mastery score. Changing subject within a conversation does not carry over the previous academic presentation.
- No real mastery or assessment data is created, even for the three supported subjects. The optional progress specimen is explicitly fictional. No verified curriculum is claimed to be loaded.
- Both languages have a labeled Languages dropdown. The ten country choices are United States, United Kingdom, Canada, Germany, Switzerland, Singapore, Australia, Netherlands, Qatar and United Arab Emirates. New selections persist stable country codes with canonical names; display labels are translated.
- Enrollment remains Grades 9–12. Earlier saved free-text countries and coding/writing/science interests remain intact. A legacy country requires an explicit supported selection only when saving an edited profile; cancelling preserves it.
- The user-supplied concept #6 board is preserved locally. The placeholder mark is replaced by icon-only ribbon-and-sparkle SVG adaptations, with separate light/dark and white/black versions. [Asset provenance and usage](BRAND_ASSETS.md) explain the adaptation.
- New messages, dialogs, utility pages and the welcome mark have restrained transform animations. Changing locale does not animate old messages again. Reduced motion disables animations, transitions and press displacement.

## Files changed for this refinement

| Files | Purpose |
|---|---|
| preview/preview.js | Country codes, academic subject policy, translated copy, demo replies, preservation of legacy data, theme-specific marks and new-message animation tracking. |
| preview/index.html | Languages/country selects, academic summaries and library starters, legacy-interest messaging and icon-only brand presentation. |
| preview/styles.css | Dropdown and subject-summary layout, contextual notices, icon dimensions and reduced-motion-aware animations. Existing central color tokens are retained. |
| preview/assets/nmi-mark*.svg | Five self-contained ribbon/sparkle assets, replacing the previous default mark and adding four named variants. |
| tools/serve_preview.py | Static allowlist expanded only for the four new SVG variants. This helper never imports tutoring modules. |
| tests/frontend-state.test.cjs | Country, academic scope, translation, grade and saved-state contract checks. |
| tests/frontend/preview.spec.cjs, onboarding.spec.cjs | Existing acceptance tests updated for dropdown controls and conversation-only responses. |
| tests/frontend/subject-scope.spec.cjs | New scope, legacy-state, subject-switching, motion and logo acceptance scenarios. |
| AGENTS.md, DESIGN.md, NMI_PRODUCT_SPEC.md | Confirmed scope and design authority, reference provenance and implementation boundaries. |
| docs/BRAND_ASSETS.md, docs/references/nmi-approved-identity.png | Preserved approved reference and asset mapping. The PNG is documentation only, not served at runtime. |
| docs/FRONTEND_REFINEMENTS.md, docs/PREVIEW_VERIFICATION.md | Current verification report and pointer from the historical report. |

## Skills applied

| Skill | Practical influence |
|---|---|
| frontend-design | Icon-only visual focal point, generous conversation space, restrained supporting controls. |
| nmi-design-system | Shared components and existing semantic tokens; one documented logo family for every screen. |
| nmi-bilingual-ui | Complete ar/en copy, translated country labels, RTL logical layout, unmirrored marks and LTR equations/code. |
| motion | Local CSS transform animations; no extra runtime, continuous decoration or paid Motion service. |
| web-design-guidelines | Native labeled controls, accessible icon links, focus states, image dimensions, reduced motion and contrast review. Applied [Vercel's current guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md). |
| nmi-frontend-quality | Desktop matrix, visual inspection, accessibility and persistence acceptance. |
| playwright-cli | Reviewed local browser automation workflow using the pinned Playwright runner and fresh project-local profiles. |
| nmi-curriculum-quality | Country availability is distinct from verified curriculum availability; no invented curricula or subject mappings. |
| nmi-tutor-testing | Questions and mock replies are not evidence of mastery or a valid assessed attempt. |
| nmi-security-privacy | Synthetic data only, bounded storage, text-safe rendering and no real credential/student access. |

All 12 installed Skills remain unchanged and validate against their recorded manifest. No Skills or dependencies were installed during this refinement. Backend-quality and reliability-testing remain available for future backend work; no backend redesign is claimed here.

## Verification

- `node tools/run_frontend_tests.cjs --max-failures=1`: **44 passed**, zero failed/skipped/flaky, in 4.0 minutes. Raw results: [.cache/frontend-results.json](../.cache/frontend-results.json).
- `node --test tests/frontend-state.test.cjs`: **7 passed**.
- `node --check preview/preview.js`: passed.
- `python -B tools/validate_setup.py` using NMI's venv: all **12** Skill schemas/manifests pass, **22** evaluation fixtures validate, and the **11 backend/rules/curriculum/dependency baseline files** are unchanged. Fixture validity is not semantic tutor accuracy.

Browser coverage includes Arabic/English × light/dark at 1280×800, 1440×900 and 1920×1080; onboarding, every sidebar destination, mock send/stop, search, code copy, MathML, hints, drafts, browser-process restart, blocked/full/corrupted/stale storage, safe text rendering, zoom/keyboard access, grade/country/subject constraints, legacy profiles, cross-topic conversations and theme-specific logo loading. Axe reported no WCAG A/AA violations on the tested screens. Reduced-motion checks cover messages, dialogs, pages and logo entrance. The static server refuses backend and traversal URLs.

Screenshots were visually inspected in both languages and themes, including the welcome, conversation, onboarding, Library, Curriculum and Progress. Examples: [Arabic dark identity](../.cache/screenshots/identity-ar-dark.png), [English light identity](../.cache/screenshots/identity-en-light.png), [Arabic curriculum](../.cache/screenshots/scope-ar-light-curriculum.png), [English dark progress](../.cache/screenshots/scope-en-dark-progress.png). No obvious layout or direction defects were found in these inspected views; this is not a complete accessibility certification.

One nonfatal Windows `ConnectionAbortedError` was logged by the development server while the logo test rapidly changed image requests. All asset loads and browser assertions passed; the static server remained operational. No application exception or failed test resulted. The backend unit suite was not rerun for these frontend-only changes; its earlier limitations remain documented in SKILLS_SETUP.md and the historical verification report.

## Open locally

From NMI, run:

```powershell
.\.venv\Scripts\python.exe -B tools/serve_preview.py
```

Open http://127.0.0.1:8765/ on a desktop browser. Use sample details only. Keep this origin/port to restore existing demo state. If the preview server is already running, simply open the address. It is bound to loopback and serves only allowlisted static assets.

## Remaining boundaries

Real AI response quality, Arabic intent recognition, curriculum sourcing, secure multi-student persistence, transactional progress/history writes and retry deduplication need separate backend work. This refinement does not fix existing Python limitations. No public-readiness claim is made. Browser verification covers local Microsoft Edge; manual screen-reader testing and other browser engines remain unverified. The earlier avatar is original placeholder art because no separate approved avatar reference was supplied.

No parent duplicate, Python tutoring module or real student file was modified. No OpenAI request, purchase, commit, push or deployment was performed.
