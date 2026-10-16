# Claude integration verification — 16 October 2026

Implementation is complete and offline checks pass. No live Anthropic inference, model-catalog request, OpenAI call or OAuth authorization was performed. No real key was read. The existing owner server on port 8766 was not restarted or used by the tests.

## Changes

New files:

- `claude_provider.py`: official asynchronous Messages streaming, structured LearningResult adapter, exact model-capability verification, hard deadline, bounded output, safe errors, usage accounting and zero retries.
- `tools/run_claude.py`: loopback launcher with both inference gates off by default, OpenAI hard-disabled, isolated one-attempt acceptance mode and explicit metadata-only account model check.
- `tests/local/claude_fixtures.py`: synthetic HTTP/SSE transport using the installed official SDK.
- `tests/local/test_claude.py`: 20 offline adapter, Flask, storage, launcher and security tests.
- `tests/local/claude_browser_server.py`: isolated synthetic browser server; remote networking denied.
- `tests/claude-browser/main-chat.spec.cjs` and `playwright.claude.config.cjs`: actual Chrome main-chat tests on separate port 8771.
- `docs/CLAUDE_API.md` and this report: owner launch/activation and verification evidence.

Updated files:

- `local_web.py`: separate Claude provider, explicit gate and server-side model, bilingual errors, usage responses; OpenAI integration retained.
- `local_store.py`: additive `request_usage` table; numeric usage saved transactionally with receipts. Existing profile/history/progress formats preserved.
- `preview/live.js`: Claude label and consent, disabled/loading/success/error states, bilingual token counts, provider-specific gate checks. No redesign.
- `requirements.txt`: pinned `anthropic==1.15.0`.
- `AGENTS.md`, `docs/LOCAL_AI.md`, `docs/backend-integration-changes.json`: documented approved provider scope and dependency change.

Installed only in `NMI/.venv`: anthropic 1.15.0 plus its new dependencies docstring-parser 0.18.0 and opentelemetry-api 1.45.1. SDK tracing is explicitly disabled. Existing installed dependencies were not replaced. `pip check` reports no broken requirements. No Skills were installed or changed.

Ignored `.cache` holds synthetic test databases, browser reports/screenshots and a source-only hash baseline. No real student database or JSON was opened for verification. Tests block CLI persistence functions and supply temporary database paths. The launcher was tested offline; the live launcher has not been started by the agent.

## Results

| Check | Result |
|---|---|
| Local backend suite | 89 passed: 69 existing plus 20 Claude tests |
| Claude Chrome main chat | 2 passed, including all four Arabic/English × light/dark combinations |
| Existing ChatGPT Chrome flow | 2 passed with mocked OAuth and streamed responses |
| Existing OpenAI API-mode Chrome flow | 2 passed with mocked responses |
| Local-session unlock browser regression | 1 passed |
| Frontend state suite | 7 passed |
| Older offline CLI suite | 11 passed, 4 expected failures, 2 skipped; no unexpected failure |
| Skill metadata/resources/manifests | All 12 valid and unchanged; 22 evaluation fixtures valid |
| Dependencies | `pip check` passed |
| Source preservation | 22 of 26 source-baseline files identical; only local_web.py, local_store.py, requirements.txt and preview/live.js changed within that baseline |
| Credential-pattern scan | No API/private-key literals in the 15 implementation/documentation files checked before this report |
| Whitespace check | `git diff --check` passed for updated tracked files |

The Claude browser test verifies main-composer submission, a visible loading state, complete response display, Arabic follow-ups, RTL/LTR, unchanged light/dark themes, token counts, reload persistence, inaccessible student model selection, interrupted/unauthorized response errors, preserved drafts/history, no browser demo persistence and no fallback when live JavaScript fails. Axe WCAG 2 A/AA and 2.1 AA checks had zero violations in all four Claude language/theme cases. Screenshots of Arabic dark and English light were inspected visually: the existing layout, logo and composer remain intact.

The adapter tests exercise the installed SDK, not just a fake `parse()` method: model metadata, serialized JSON schema, SSE completion, strict assessment validation, max-token/refusal/malformed/truncated responses, HTTP failures, header timeout and a stalled mid-stream deadline. Errors expose safe codes only. Duplicate failed/successful request IDs never repeat a paid POST. Atomic storage-failure and additive-migration tests preserve earlier synthetic history and progress. Both paid gates, missing key/model, call budgets, CSRF/origin/session protection, owner-only provider/model selection and blocked OpenAI factories are covered.

The four pre-existing expected CLI failures are corrupt JSON handling, wrong JSON shape rejection, graceful timeout handling and atomic separate progress/history writes. The two skips concern future CLI multi-student storage and request deduplication. These are not claimed as fixed; the separate Flask transactional path is tested independently.

## Skills actually applied

- `nmi-backend-quality`: adapter preserves `ask_ai`/LearningResult contracts; HTTP/provider selection stays outside teaching logic.
- `nmi-security-privacy`: server-only key, locked owner configuration, consent, local session/CSRF checks, sanitized errors and no student/key logging.
- `nmi-reliability-testing`: malformed streams, total deadlines, duplicate receipts, rollback, corrupted storage and migration tests.
- `nmi-tutor-testing`: questions/hints/confusion cannot become incorrect attempts; valid correct/incorrect assessments and bilingual follow-ups preserve context.
- `nmi-bilingual-ui`: Arabic/English copy, RTL/LTR and localized token-count presentation.
- `nmi-frontend-quality`: main-chat states, four locale/theme cases, persistence, accessibility and visual review.
- `playwright-cli`: existing project-local Playwright/Chrome workflow, synthetic fixtures, local artifacts, no attachment to the owner's browser/profile.

Other installed Skills were validated and reused by reference where appropriate, without loading unrelated design/animation work or changing them. AGENTS.md was read; its historical statements about Flask being future work are superseded by the existing code and the owner's current authorization.

## Remaining checks before real use

Owner account access to `claude-sonnet-5-5`, credit balance, network/TLS connectivity, live response correctness and actual usage remain unverified. The first live request requires separate explicit approval. Use the commands in [CLAUDE_API.md](CLAUDE_API.md); the default launch cannot infer. The owner-only metadata check is not an inference request, but was also intentionally not run here.

This remains a one-tester local prototype with one saved conversation per store, not a deployed multi-user educational service. The UI honestly describes that limitation. No curricula or student assessment policies were expanded. No real records were migrated/deleted, no parent duplicates modified, and no Git staging, commits or pushes performed.
