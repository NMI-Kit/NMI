# NMI product specification

Approved requirements source: the user's master product specification, 12 October 2026. Implementation evidence belongs in docs/PREVIEW_VERIFICATION.md; this contract is not a claim that every capability is complete.

**Current authority update — 15 October 2026:** [MASTER_BRIEF_STATUS.md](docs/MASTER_BRIEF_STATUS.md) supersedes conflicting older requirements below. Israel-first scope, ten revised countries, expanded planned subject catalog and the latest no-floating-star logo preference are approved requirements, not completed features. Phase 1 connects the main chat to Flask; real authorization/model/inference acceptance remains pending. Older sections are historical design context and must not override this update.

## Product boundary

NMI is a premium, conversation-first adaptive learning assistant. Desktop V1 supports screens 1280px and wider, Arabic/RTL and English/LTR, light and dark themes, and enrollment in Grades 9, 10, 11 and 12 only. No lesson selection is required before asking a question. Python learning modules and existing student files remain unchanged during design work. The frontend stays HTML, CSS and vanilla JavaScript.

Use a single configurable supported-grade list, separate from curriculum data. Future younger-grade enrollment requires an explicit scope change, validated country/grade/subject sources and tests. Do not generate official curriculum requirements for missing or unsupported coverage.

## V1 subject and country clarification — 13 October 2026

The main chat accepts any topic. Official curriculum alignment, structured skill assessment, mastery percentages and academic progress tracking are eligible only for Mathematics, Physics and Chemistry. Other topics receive normal tutor conversation and retain conversation history, without academic assessment, mastery scores or unsupported curriculum availability. More academic subjects can be introduced through an explicit capability-list extension, verified source coverage and tests. The local preview still uses mock replies; this requirement does not authorize connecting live AI or changing the Python core.

Academic eligibility is not curriculum availability: even an eligible subject must show unavailable until a reliable source is verified for country, grade and subject. Questions, hints and confusion never become assessed attempts, including within the three eligible subjects.

The confirmed ten countries are United States (US), United Kingdom (GB), Canada (CA), Germany (DE), Switzerland (CH), Singapore (SG), Australia (AU), Netherlands (NL), Qatar (QA) and United Arab Emirates (AE). Display names are translated; new onboarding uses stable codes. Existing free-text country values and earlier non-academic interests must remain readable without silent deletion or reclassification. Editing a legacy profile requires an explicit supported-country selection. Selecting a country does not imply curriculum coverage.

Arabic and English are selected through a labeled Languages dropdown. All previous profile, progress, curriculum, library, settings, onboarding, returning-user persistence, desktop and theme requirements remain in force. Animations must be implemented and tested, honor reduced motion, and avoid replaying entire conversation histories on preference changes.

Brand requirement: approved concept #6, icon only, in light/dark variants. The user supplied the ribbon N and sparkle identity board on 13 October 2026; it is preserved at docs/references/nmi-approved-identity.png. The preview uses documented SVG adaptations with separate light/dark and white/black assets. See docs/BRAND_ASSETS.md. The image's extra subject examples are visual references, not authorization to expand the three-subject academic scope.

## Experience

- Sidebar: original NMI branding, New Chat, Search Chats, Conversation History, Progress, Curriculum, Library, Profile and Settings.
- Welcome: centered NMI identity, a clear invitation to ask, and a prominent composer. Conversation: readable student/assistant turns, steps, LTR mathematics and code, contextual hints and short checks. Learning tools remain secondary.
- First local visit: ask for Arabic/English, a demonstration display name, country of study and Grade 9–12. No email or password. Explain browser-local demo storage before saving. Return visits with valid saved state skip onboarding.
- Profile: name, optional original illustrated avatar, grade, country, preferred language, subject interests, subject/skill progress, strengths, recurring weaknesses, history and Continue Learning. The exact avatar reference has not been supplied; no exact-match claim is permitted.
- Empty progress remains empty. An explicitly labeled fictional specimen may demonstrate progress presentation; it must never become a student's assessment.

## Local prototype storage

Only synthetic profile details and demonstration conversations belong in this preview. Store versioned, bounded, validated demo state plus language/theme preferences in origin-local browser storage. No credentials, authentication tokens, real student imports, backend writes or telemetry. All demo text is rendered as text, never executable markup. Storage is not identity or isolation between people sharing a browser profile.

Restore onboarding, language, theme and demo conversations across browser-process restarts at the same origin. Invalid, unsupported-version or oversized saved state must not crash or be silently overwritten. Explain storage failure and allow explicit clearing of preview data only. Blocked/full storage must leave the current demo usable without claiming it was saved. Simultaneous tab changes must be detected before overwriting another tab's state.

## Adaptive teaching contract (future tutor, not a mock capability)

Classify question, answer, hint request, confusion and ambiguity using exercise context. Arabic spelling mistakes are clues, not incorrect learning attempts. A question, hint or confusion must never lower mastery. Assess only grounded subject/topic/skill fields and boolean assessment results. Track verified recurring weaknesses separately from unverified inferences.

For a Grade 10–12 learner missing an earlier foundation: preserve enrolled grade and the original question; identify the prerequisite with evidence; explain one concept at an appropriate level; give a short comprehension check; record only a valid assessed response against that prerequisite skill; return to the original task after sufficient understanding, or offer another small scaffold. Do not relabel the learner as a younger-grade student. Earlier foundation support is not enrollment in Grades 1–8 or a claim of official coverage.

Future records need stable skill IDs, prerequisite references, provenance, evidence, original-task context and a resumable remediation state. Validate dangling references and cycles. Country, grade and subject mapping requires identifiable authoritative sources. No source means unavailable/unverified, with the existing fallback preserved.

## Future secure integration gate

Authorized local exception, 13 October 2026: `local_web.py` provides a loopback-only single-tester experiment with separate SQLite storage and explicit paid-call activation. See docs/LOCAL_AI.md. It does not expose or migrate CLI JSON records, does not implement multi-student accounts, and is not a public integration. The production requirements below remain in force for broader use.

Do not expose singleton student.json/progress.json/chat_history.json as a public service. Before integration: student-scoped server repositories, verified identity and per-record authorization, transactions, idempotency, localized failures, validated inputs, privacy-safe logs and migration/rollback design. Remember Me uses expiring/rotatable server sessions and Secure, HttpOnly, SameSite cookies with CSRF protection. Logout and revoke-session must invalidate server sessions. Never store passwords or auth tokens in localStorage. Detailed security implementation and testing require a separate authorized task.

## Measurable acceptance

| ID | Required evidence |
|---|---|
| UX-1 | Welcome, conversation and all sidebar destinations function without selecting a lesson. |
| UI-1 | Arabic/English × light/dark at 1280×800, 1440×900 and 1920×1080; no unexpected clipping; composer reachable. |
| ON-1 | Exactly four selectable grades (9–12); invalid/blank/unsupported values rejected at input and saved-state boundaries. |
| ON-2 | First-time form works in both languages; valid returning demo skips it; optional avatar can be off. |
| PR-1 | Profile and progress screens contain required fields, truthful empty states, and explicit labels on fictional examples. |
| PS-1 | A new browser process with a fresh project-local test profile restores completed onboarding, preferences and demo conversation content. Reload alone is insufficient evidence. |
| PS-2 | Missing/corrupt/wrong-version/oversized/blocked/full storage and stale-tab writes handled without silent data replacement. |
| CH-1 | Mock send/stop, search, independent chats, draft preservation, code copy, mathematics, hints and checks tested. No actual tutor assessment. |
| A11Y-1 | Automated WCAG A/AA checks on tested screens; keyboard/focus/dialog, reduced-motion and zoom checks; screenshots visually inspected. No blanket conformance claim. |
| SAFE-1 | No external runtime requests or student-file access; backend hash baseline unchanged; malicious text cannot execute. |
| EVAL-1 | Offline dataset covers all supplied scenarios, records provenance and per-case unevaluated/results status. Mock plumbing tests are reported separately from real tutor quality. |
| SUB-1 | Academic selections and progress specimens contain Mathematics, Physics and Chemistry only; arbitrary-topic chats and prior history remain usable. |
| SUB-2 | Coding, writing, history and other conversations create no mastery/assessment data or progress indicators; unsupported curricula are never shown as loaded. |
| COUNTRY-1 | Ten confirmed translated country options; stable-code validation; legacy stored country/interests preserved. |
| MOTION-1 | New-message and dialog animations tested normally and under reduced motion; changing language does not replay old messages. |
| BRAND-1 | Verify the supplied approved concept #6 reference and its icon-only light/dark variants before claiming brand completion. |

Do not call the prototype complete until these gates are verified. Wait for design approval before connecting real student data or AI.
