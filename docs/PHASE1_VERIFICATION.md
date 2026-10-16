# Phase 1 verification and resume point

15 October 2026. The core local chat repair passed offline tests in real Chrome. **No real OAuth authorization or AI inference occurred. NMI is not yet accepted as a working live tutor.**

## Implemented

- Main NMI composer/transcript now uses Flask; connection/profile setup is in Settings. Themes, language changes, navigation and reload preserve the server transcript. Real replies never enter demo browser storage.
- All scripted response paths and demo restore/save are blocked on Flask, including when the live script fails. The separate static preview remains functional.
- Private fragments are validated and removed. A signed non-authorizing cookie round trip precedes the single-browser claim. Stale-link and delayed-response races are handled. Losing cookies after a completed claim still requires restarting; second-browser access remains denied.
- Browser waits have deadlines. Unknown outcomes retain the draft/request ID. Read-only receipts reconcile pending/done/failed/missing outcomes without repeating inference. A confirmed reply displays even if the next state refresh fails.
- Terminal-only control validates an account-authorized model and arms one request without restarting OAuth. No student model/activation endpoint exists.
- `tools/run_chatgpt_test.py` isolates the first acceptance in a fresh fictional database. It starts inference off, hard-disables paid API, originally accepted only the approved Arabic question and permitted one attempt without rearming. The later owner-requested conversation update removed the text/language/intent restriction and added a separate persistent multi-turn launcher; see CONVERSATION_MODE_VERIFICATION.md.
- Existing tutoring rules, LearningResult, curriculum content, JSON helpers, OAuth/provider implementation and SQLite transaction logic remain unchanged.

## Files changed

Application: `local_web.py`, `preview/live.js`, `preview/live.css`, `preview/preview.js`.

Tooling/tests: `tools/run_chatgpt_test.py`, new `tests/local/test_session_receipts.py`, preflight fixture updates in `tests/local/test_local_web.py`, `test_chatgpt.py`, `test_unlock.py`, synthetic-only budget update in `chatgpt_browser_server.py`, new `tests/phase1-browser/main-chat.spec.cjs`, migrated local/unlock/ChatGPT browser specs, and the installed-Chrome path in `tests/frontend/onboarding.spec.cjs`. New `playwright.phase1.config.cjs`; existing local/unlock/ChatGPT/static Playwright configs updated to the installed Chrome executable with Chromium sandboxing enabled. Static-server reuse requires explicit `NMI_REUSE_STATIC_TEST_SERVER=1`.

Documentation: `AGENTS.md`, `DESIGN.md`, `NMI_PRODUCT_SPEC.md`, `docs/CHATGPT_SIGN_IN.md`, `docs/LOCAL_AI.md`, `docs/MASTER_BRIEF_STATUS.md`, `docs/TECHNICAL_AUDIT_2026-10-15.md`, this report. Source recovery copies/hash manifest are in ignored `.cache/phase0-20261015/`; no student records or credentials were copied.

No dependencies/Skills installed. No parent duplicates, student data, Git index, commits, pushes or deployment changed. Existing unrelated Git changes remain intact.

## Verified results

| Check | Result |
|---|---|
| Python local integration | 65 passed; isolated data, socket denial, mocked OAuth/structured streams |
| Legacy CLI | 11 passed, 4 expected failures, 2 skipped |
| Frontend state | 7 passed |
| Main-chat Chrome scenarios | 2 passed: mocked OAuth/chat/errors; failed script cannot produce demo fallback |
| Unlock Chrome scenario | 1 passed: fragment navigation, invalid/stale links, port cookies, refresh, delayed-state race, lost-session error, second browser |
| API-adapter Chrome scenarios | 2 passed with mocks only; no paid API request |
| Static-preview Chrome regressions | 44 passed, including onboarding, themes/locales, storage failures, browser restart, motion/reduced motion and zoom |
| Accessibility | No axe A/AA violations in the tested live language/theme states |
| Package/setup | pip check passed; 12 Skills validated; 22 semantic cases valid but not live-evaluated; learning-code baseline unchanged |

Browser tests found and fixed main-transcript keyboard access and a DOM AbortError incorrectly treated as a confirmed server rejection. Old pane-specific assertions were migrated to the actual main composer. Tests use synthetic OAuth pages/transports and prohibit external provider traffic.

Visually inspected `.cache/screenshots/phase1-ar-light.png`, `phase1-en-dark.png` and the initial failure screenshot. The suite captures all four language/theme combinations. Both retain the main conversation, bottom composer, themes and RTL/LTR positioning. This is not a blanket accessibility certificate or acceptance of future branding changes. Real replies remain inert plain text; rich math/code rendering is deferred.

The running static preview was verified byte-for-byte against current JavaScript before reusing its listener for regression tests. The old port-8766 Python process was verified to run local_web.py with inference disabled, then stopped. The isolated acceptance launcher is now running in a new interactive PowerShell terminal (terminal PID 7244, server PID 17340). Public checks confirm sign-in enabled, inference disabled and the exact current live.js bytes served. Existing student data were not opened; the launcher created a fresh synthetic database. No actual authorization or inference was initiated.

Earlier browser attempts hit approval-review usage limits, then restricted-process Chrome startup errors. Later reviewed execution succeeded with isolated profiles and Chromium sandboxing enabled. No approval check was bypassed. Parallel workers hit usage limits; the primary agent completed the repairs/tests directly.

## Live acceptance remains pending

| Milestone | Status |
|---|---|
| Local unlock in real browser with synthetic credentials | Passed |
| New isolated port-8766 server | Ready; owner still needs to open its private link and authorize |
| Actual ChatGPT authorization/plan grant | Not performed |
| Actual authorized model | Not retrieved/selected |
| Real structured inference and main-chat reply | Not performed |
| Real synthetic conversation saved/reopened | Not performed; mocked persistence passed |

## Earlier acceptance procedure (superseded for normal conversations)

Use CHATGPT_SIGN_IN.md for the current launch commands. The following records the original acceptance workflow, not a restriction on normal tutoring.

1. The new owner terminal is already running. If it has since stopped, from NMI run `.\.venv\Scripts\python.exe -B tools/run_chatgpt_test.py`. Never start a second listener over an existing process.
2. Open the new complete private link in one Chrome profile. Click Tutor connection.
3. User personally clicks Continue with ChatGPT and approves official permissions. Never enter their password or approve for them.
4. In the same terminal run `status`, then `models`. Stop if access/catalog fails.
5. After explicit approval for one inference, enter `arm EXACT_AUTHORIZED_MODEL_SLUG`. Refresh NMI connection status, choose Arabic/question intent, review consent, then send «لماذا تسقط الأشياء على الأرض؟ اشرح لي ببساطة.» once.
6. Verify completed structured response, actual main-chat reply, two saved messages, zero attempts and persistence after reload. Stop on failure before another inference; do not restart to reset the budget.
7. Proceed to Phase 3 only after that real milestone. Follow MASTER_BRIEF_STATUS.md for subsequent phases.

Full activation/troubleshooting: [CHATGPT_SIGN_IN.md](CHATGPT_SIGN_IN.md).

## Remaining limits

Legacy expected failures expose real CLI corruption/type handling, uncaught timeout and non-atomic persistence defects. No verified official curriculum exists. Intent plus prior assistant context is weaker than an evidence-grounded active-exercise contract; curriculum-grounded mastery is not claimed. Account/model/schema compatibility remains unverified. OAuth errors remain broad sanitized categories. Provider event timing is not a hard wall-clock cancellation guarantee.

Backend multi-conversation/pinning, adaptive memory, revised country/catalog/onboarding and latest logo refinements remain later phases. The backend/reliability Skills retain some stale future-Flask wording; current source/audit take precedence.

Applied Skills: backend-quality for injected contracts; security-privacy for ownership, credentials and billing boundaries; reliability-testing for receipts/fault preservation; tutor-testing for assessment boundaries and honest mock claims; bilingual-ui for paired copy/RTL; design-system for shared shell/tokens; frontend-quality and playwright-cli for actual browser checks; web-design-guidelines for semantic controls/focus/errors; OpenAI Docs for the official route. Frontend-design was read for constraints; no major redesign or new animation system was implemented.
