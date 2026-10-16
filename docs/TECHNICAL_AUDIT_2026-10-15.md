# NMI technical audit — 15 October 2026

## Authority and recovery

The owner's master brief attached on 15 October is the current product authority. Execute its phases in order: audit, core live chat, one explicitly approved real test, adaptive intelligence, onboarding, Israeli curriculum, interface refinement, final review. Existing specifications contain older country/subject scope; those are not evidence that the newer scope is implemented.

Source-only recovery copies and a SHA-256 manifest are in ignored `.cache/phase0-20261015/`. No student records, credentials or runtime databases were copied. Existing parent duplicate changes and untracked work remain untouched. No commit was created.

## Actual architecture

- `main.py` is the legacy singleton JSON CLI. `student_profile.py`, `progress.py` and `chat_history.py` resolve their files inside NMI. They are not the website's data store.
- `ai_test.ask_ai()` assembles the existing teaching rules, curriculum fallback, profile, history and progress. Its injected client/storage/model contract supports Flask without changing the CLI persistence paths.
- `LearningResult` validates nonempty assessment identifiers and boolean assessment values. Missing/invalid responses do not update website history or progress.
- `local_web.py` supplies loopback-only Flask, capability-to-cookie unlocking, Origin/CSRF checks, owner-selected provider/model and a one-request budget. Paid API mode is separately disabled by default.
- `chatgpt_auth.py` implements official OAuth with PKCE, state, nonce, signed identity checks and single-account binding. Tokens remain in memory. `chatgpt_provider.py` uses official structured streaming, `store=false`, no automatic retries and no paid fallback.
- `local_store.py` stores one local owner's profile, one conversation, attempts and request receipts in SQLite. Successful history/progress/receipt writes are atomic. This is not multi-user authentication or multiple saved conversations.
- The static preview uses explicitly synthetic browser storage. The current Flask adapter adds a separate technical chat pane instead of using the main composer. Demo and real history are disconnected.

## Confirmed defects before implementation

1. Main composer only transfers a draft to the separate live composer; browser tests assert the separate pane, not the main chat.
2. Demo hint/check handlers can generate scripted replies on Flask despite the main submit guard.
3. Frontend fetch has no deadline. A hung request can leave loading indefinitely.
4. Successful chat POST discards its returned reply, clears the draft and then depends on another state fetch. A failed refresh hides an already saved response.
5. Switching locale/theme or sidebar sections can restore demo content over the live experience.
6. A first claim with a lost/blocked cookie locks the process. A second browser is intentionally rejected; weakening this protection is not a fix. An unchanged access fragment indicates unloaded/stale/crashed frontend code, because current code removes it before its claim request.
7. Inference/model configuration is captured at launch. Restarting to enable it loses in-memory OAuth tokens. A server-side developer activation path is needed for authorize-first testing.
8. The provider's event deadline is checked between reads, not a strict wall-clock deadline. Browser waiting and unknown outcomes need bounded, non-retrying recovery.
9. Arabic connection copy still asks the student to select a model. Models must remain developer-only.

## Genuine capabilities and known gaps

All current curriculum lookups use an explicit fallback: `curriculum.txt` contains no supported sections. There is no verified Ministry curriculum ingestion or retrieval. The three-subject assessment scaffold is not proof of curriculum-grounded mastery. A prior assistant message plus answer intent is not sufficient evidence of an active assessed exercise; later academic work must strengthen this contract.

`subject_router.py` is unused keyword logic. Arabic typo understanding, adaptive memory, confidence estimates, multiple conversations, pinned real chats, expanded onboarding and Israel-first academic coverage are not implemented merely because preview controls or Skills exist. The 22 semantic tutor examples remain unevaluated against a real model.

All 12 project Skills exist. Backend/reliability Skill wording describing Flask as future work is stale. Current logo assets are adaptations, not verified original artwork; no exact hand-drawn sketch file was available. Branding work is deferred behind live chat.

## Independently verified baseline

- Local backend: 58 passed, isolated temporary data and mocked network/provider responses.
- Legacy CLI: 11 passed, 4 expected failures, 2 skipped. Expected failures expose corrupt/wrong-shaped JSON, uncaught timeouts and non-atomic persistence; they are not implemented protections.
- Earlier reports claim 4 browser scenarios and 7 state tests. They must be rerun against the new main-chat implementation. Those browser scenarios used mocks and the old separate composer.
- Actual running server: loopback port 8766, sign-in enabled, inference disabled. No real authorization, authorized model, live inference, rendered real reply or real acceptance persistence has been verified.
- Browser launch was blocked by automatic approval review reaching a usage limit. No attempt was made to bypass that review. Browser validation remains pending until the reviewed tool can run.

## Implementation checklist

- [x] Audit actual components, Skills, test claims and legacy failures.
- [x] Preserve a source recovery point without touching student data.
- [x] Use one main chat and protect every scripted response path on Flask.
- [x] Bound pending states; reconcile uncertain outcomes without repeating inference.
- [x] Verify cookie establishment before consuming the private launch claim; explain stale/claimed-session failures.
- [x] Support terminal-only account model selection and one-shot activation after OAuth.
- [x] Rerun offline contracts, frontend state tests and actual browser regressions. Current evidence is in PHASE1_VERIFICATION.md; the earlier browser-tool restriction was resolved through reviewed execution.
- [ ] User completes official OAuth personally; verify account-authorized models.
- [ ] After explicit approval, send exactly one approved synthetic question, validate/render/save/reopen it; stop on failure.
- [ ] Only after that milestone, proceed to adaptive learning, onboarding, curriculum and design phases.

No real AI success is claimed by this audit.
