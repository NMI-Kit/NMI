16 October: [Claude integration](CLAUDE_API.md) adds an independent, disabled-by-default Anthropic provider in the main chat. Use its dedicated launcher for isolated testing; it disables both OpenAI providers. No live Anthropic request has been made.

15 October repair: ChatGPT activation and owner-only model configuration are documented in [CHATGPT_SIGN_IN.md](CHATGPT_SIGN_IN.md). Paid API billing now requires explicit `NMI_ENABLE_PAID_API=1`; keep it `0` for ChatGPT plan tests. Scripted preview replies are disabled on the Flask server. The sections below describe the original integration; the newer sign-in guide takes precedence for launch and model controls.

# First local AI conversation — offline integration

**Current phase-1 procedure, 15 October:** use [CHATGPT_SIGN_IN.md](CHATGPT_SIGN_IN.md) and `python -B tools/run_chatgpt.py` for persistent ChatGPT conversations (`--acceptance` for an isolated one-request test). Neither mode restricts question wording. Flask now uses the main NMI composer, not the separate pane described historically below. Paid API stays disabled. The first live authorization/model/inference remains unverified. Do not use the historical API-key activation instructions for the ChatGPT test. Current evidence is in [PHASE1_VERIFICATION.md](PHASE1_VERIFICATION.md).

14 October update: [ChatGPT plan integration](CHATGPT_SIGN_IN.md) adds a separate official OAuth option. The API-key activation steps below still apply only to API mode. Sign-in and inference are separately disabled by default, and neither has been tested live. No exposed key may be reused.

13 October 2026. **No real OpenAI API request has been made.** The application defaults to AI disabled. The first paid test is a manual action for the owner, using fictional student details and non-sensitive questions.

## What runs where

```text
Browser on 127.0.0.1:8766
  private launch link -> one claimed HttpOnly browser session
  Local AI pane -> consent + message + intent + request ID
      Flask validation / origin / CSRF / budget gate
          ask_ai(..., storage=buffer, ai_client=server_client)
              existing tutor_rules.txt + existing LearningResult
              OpenAI Responses parse (only when explicitly enabled)
          SQLite transaction: history + valid attempt + request receipt
      localized reply/error -> safe text in the existing NMI layout
```

The unchanged static design demo still runs on port **8765**, with no API connectivity. The Flask site on **8766** serves the same HTML, CSS, logo and JavaScript and injects `live.js` / `live.css`. A Local AI button opens a separate conversation pane; returning to demo restores its synthetic UI. Existing demo data is not imported into the local AI profile. Real replies are never placed in demo localStorage.

This prototype supports **one local tester and one saved real conversation**, not multiple students or accounts. Its country/grade profile is set once and cannot be reassigned through HTTP. There is no student ID/path parameter. One claimed browser session can access the database; another browser profile is rejected even if it later receives the same launch link. Restart the server to establish a new owner session for the **same tester**. Existing history remains. Do not share this server or computer session with other students.

## Changes

| File | Purpose |
|---|---|
| ai_test.py | Lazy client initialization; optional injected client/model/storage and web-only safety/assessment policy. Five positional CLI arguments and return type remain compatible. Failed web responses raise a typed error before persistence. |
| local_web.py | Flask app, fixed loopback launcher, single-process lock, one-browser capability claim, session/CSRF, input validation, localization, request limits and provider failure mapping. |
| local_store.py | Independent SQLite state, buffered changes, atomic conversation/progress/receipt commit and request deduplication. |
| preview/live.js, preview/live.css | Bilingual opt-in AI pane, consent, separate profile, message intent, real transcript, attempt counts, draft/error handling and same-request recovery. Existing design assets and demo source are unchanged. |
| requirements.txt | Added verified `Flask==3.1.3` to the existing OpenAI/Pydantic pins. Installed official wheels in NMI/.venv only. |
| .gitignore | Excludes .local-data, SQLite files/journals and project environment files. |
| tests/local/* | Mocked backend integration, security, persistence, error and browser-server fixtures. |
| tests/local-browser/live.spec.cjs, playwright.local.config.cjs | Actual browser -> Flask -> ask_ai -> fake provider -> SQLite acceptance. |
| tests/offline/test_backend_contracts.py | Test injection updated for lazy initialization; skip descriptions distinguish CLI gaps from new Flask coverage. |
| AGENTS.md, DESIGN.md, docs/LOCAL_AI.md | Current architecture, scope, safeguards and activation instructions. |
| tools/validate_setup.py, docs/backend-integration-changes.json | Preserve the original hash baseline while checking the two explicitly recorded integration changes (ai_test.py and requirements.txt); all other baseline files must remain unchanged. |

The existing `LearningResult`, tutor rules, curriculum content, progress algorithms, JSON helper modules, parent duplicates and real student JSON files were not changed. No automatic migration or deletion occurs.

## Activation — first paid request (owner only)

Use an adult/supervised tester and fictional questions first. Confirm an API model ID in your OpenAI account that supports **Responses and Structured Outputs**, and check its pricing/account access. The previous CLI hardcoded model is not assumed to be available. This adapter deliberately requires `OPENAI_MODEL`; it makes no model-list request or silent model fallback.

Open a private PowerShell terminal, then run:

```powershell
Set-Location 'C:\Users\ahmad\OneDrive\Desktop\studdy app\NMI'

$nmiSecureKey = Read-Host 'Enter OPENAI_API_KEY (hidden; never paste it in the website)' -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new('', $nmiSecureKey).Password
$env:OPENAI_MODEL = Read-Host 'Enter the exact supported API model ID'
$env:NMI_ENABLE_AI = '1'

try {
    .\.venv\Scripts\python.exe -B local_web.py
} finally {
    Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:NMI_ENABLE_AI -ErrorAction SilentlyContinue
    Remove-Variable nmiSecureKey -ErrorAction SilentlyContinue
}
```

1. Open the **private loopback link printed by this server**. Its fragment is a temporary local access capability, **not** your OpenAI API key. Do not share it. The frontend removes the fragment immediately after reading it; it is never sent as a URL to the server.
2. Set your local test country and Grade 9–12. Only the ten approved countries are selectable. No name, email, birthday or password is collected for the live profile.
3. Select Arabic or English in Languages. Read the disclosure and tick the consent checkbox.
4. Enter a harmless question such as “Help me understand why one half is greater than one quarter.” Keep **Question** selected, then click **Send to AI**. **This is the first action that can incur an API charge.** Startup, page load, profile setup and reading history do not call OpenAI.
5. Review the reply and account usage. The server allows **one attempted provider call per launch**. A question should add two history entries and zero attempts. No mastery percentage is displayed or inferred.
6. Stop with Ctrl+C. The `finally` block clears the key from this terminal's environment. For a later assessed answer, deliberately restart, open the new private link, select **Answer to an exercise**, and answer a tutor exercise already in history. Do not label an ordinary question as an answer.

To inspect the local interface with paid calls locked, set `$env:NMI_ENABLE_AI = '0'` and run the same Python command. No key is needed. Use port 8766; the old 8765 preview remains mocked.

Do not use `flask run`, bind to 0.0.0.0, start a tunnel, enable debug/reload, or deploy this prototype. Use `local_web.py`, which pins 127.0.0.1:8766 and prevents a second launcher sharing its database. The launcher is Windows-specific because it uses the existing Windows environment's process file lock.

## Failure and cost behavior

- Missing key, missing/invalid model configuration and disabled AI fail without an API request. Keys are read only by the server client factory at explicit send time. The endpoint is pinned to `https://api.openai.com/v1`; arbitrary `OPENAI_BASE_URL` is ignored.
- The SDK has a 35-second timeout and **zero automatic retries**. Output is capped at 1,800 tokens. Previous context is bounded to the last 20 messages and 100 attempts, while the full accepted local transcript is retained up to 100 exchanges. A six-per-minute guard exists in addition to the one-call production-launch limit.
- Timeout/connection/rate-limit/provider failures, unavailable/unsupported models, refusal/missing/incomplete/invalid parsed output and storage faults return generic localized errors. Provider error details, request bodies and credentials are not logged or returned.
- Failure does not append a chat exchange or attempt. Success commits both with the request receipt in one SQLite transaction. Disk failure between updates rolls the transaction back.
- Duplicate request IDs return the existing reply, without another provider call or attempt. Reusing an ID for different text is rejected. A lost browser response offers **Check / retry the same request** using the same ID; no automatic resend occurs. Failed receipts are not retried as new API calls. An interrupted in-flight receipt becomes “uncertain” on restart.
- A timeout, connection loss or local save failure **can still incur provider charges**. Local idempotency cannot guarantee provider-level exactly-once billing. Inspect the conversation and account usage before deliberately starting a new request. Drafts/unknown request IDs are held only in the current tab; leaving warns, but closing loses that unsent state.

## Assessment and educational boundaries

The original tutor rules and structured schema are preserved. Web-only supplemental instructions reinforce Grades 9–12, prerequisite help without changing enrollment, age-appropriate behavior, not requesting identifying information, and not inventing official curriculum requirements.

Only an explicitly selected **Answer** with prior assistant context and a valid `LearningResult` can record an attempt, and only for exact canonical `mathematics`, `physics`, or `chemistry` subjects. Questions, hints, confusion, first-turn answers and unsupported subjects do not record attempts even when a mocked model mislabels them. Ordinary discussions are still saved. Invalid assessment fields reject the whole failed exchange without filling in missing values.

These checks do not prove that an AI assessment is correct, that the prior assistant message was a suitable exercise, or that skill IDs match an official curriculum. Verified curriculum records and a structured exercise/skill registry remain future work. No curriculum is fabricated. Safety prompting is not a validated moderation system: keep this first test supervised and synthetic. Real minor accounts require additional safety evaluation, authorization/consent policy, retention controls and moderation review before broader use.

## Privacy and access limits

Records are in **NMI/.local-data/tutor.sqlite3**, ignored by Git and never served as a file. This is plain local SQLite, not encrypted storage. The workspace is inside OneDrive: operating-system/cloud-folder sync settings may copy local files independently of this app. Use fictional test data; do not treat loopback binding as a cloud-storage guarantee.

The app implements host/origin checks, a random per-launch capability, one claimed signed session, HttpOnly/SameSite=Strict cookies, eight-hour session expiry, CSRF protection, no CORS access, bounded JSON and allowlisted static assets. Secure cookies are intentionally not used on this **HTTP loopback** prototype; production would require HTTPS and a different authentication design. Anyone controlling your OS account or browser profile can access local data; this is not multi-user security.

Replies are displayed with textContent, without model-generated HTML, scripts, executable tools, image fetches or link activation. This first live pane uses plain text, including raw code/formula notation; the demo's rich MathML/code examples remain unchanged. API secrets never appear in JavaScript, cookies, localStorage or database payloads.

`store=False` is set for Responses API storage. This does not assert zero provider retention or replace OpenAI account data controls. The request includes message history, country, grade, language, existing progress and tutor/curriculum context; the name supplied to the model is the fixed generic “Learner.”

Implementation references: [Flask security guidance](https://flask.palletsprojects.com/en/stable/web-security/), [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data). The installed OpenAI 3.28.0 SDK's actual parse signatures and exception types were inspected locally.

## Offline verification

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/local -v
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/offline -v
node tools/run_frontend_tests.cjs --config=playwright.local.config.cjs
node --test tests/frontend-state.test.cjs
.\.venv\Scripts\python.exe -B -m pip check
```

Final results:

- **21/21** local Flask integration tests pass, including concurrent sends, second-launcher exclusion, session expiry/tampering, malformed state, transactional rollback, supported country/grade pairs, rate limits, duplicate requests, and provider failure mappings.
- **1/1** complete browser integration scenario passes across Arabic/English × light/dark at 1280×800 and 1440×900, with zero axe WCAG A/AA violations on the tested screens. It covers consent, return/reload, safe AI text, a lost response and same-ID recovery, successful assessment persistence, timeout preservation, rejected second-browser access, and demo/real-data separation. Zero page JavaScript exceptions or external browser requests were observed. Raw results: [.cache/local-browser-results.json](../.cache/local-browser-results.json).
- **7/7** existing offline frontend-state tests pass.
- Legacy CLI: **11 pass**, **4 expected failures** (corrupt/wrong-shaped JSON, unhandled timeout and non-atomic JSON persistence), **2 deferred cases** (multi-user storage and CLI request IDs). These are preserved CLI limitations, not failures of the new isolated Flask adapter.
- `pip check`, JavaScript syntax, strict LearningResult schema conversion and setup validation pass. All **12 Skills** still match their manifests; the authorized two-file backend change record matches, and all nine other original baseline files are unchanged.

The final [Arabic light](../.cache/screenshots/local-ar-light.png) and [English dark](../.cache/screenshots/local-en-dark.png) browser screenshots were visually inspected, including the fixed composer, original marks, RTL/LTR text, consent and safe literal model output. The static demo's HTML/CSS/JS, tokens and logo files were not changed in this integration; its prior 44-test run was not repeated without changes to those files.

All new backend tests deny outbound sockets and use fresh .cache temporary data. The browser fixture injects a fake provider and cannot make outbound connections. No real key is needed, loaded or used in these tests. No production local database was opened or migrated during the tests. Real model quality, account/model access, moderation effectiveness and billing remain untested. Manual screen-reader and non-Edge browser testing remain future work.

Skills applied: nmi-backend-quality (adapter contracts), nmi-security-privacy (local session and record boundaries), nmi-reliability-testing (faults/atomicity/retries), nmi-tutor-testing (intent/valid assessment gates), nmi-curriculum-quality (no invented provenance), nmi-bilingual-ui and nmi-frontend-quality (translated UI/accessibility), and OpenAI Docs (SDK behavior and retention limits). Existing Skills' historical “Flask not implemented” notes describe the prior baseline; this document and updated AGENTS.md describe the authorized new prototype.

No commit, push, public deployment, unrelated source change or real API call was performed.
