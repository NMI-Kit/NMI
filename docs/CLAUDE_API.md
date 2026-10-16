# Local Claude tutoring

Implemented 16 October 2026. Offline testing only: no real Anthropic request, account credential, or student file was used.

## Integration

The existing main composer posts to Flask `/api/chat`. With `NMI_AI_PROVIDER=claude`, Flask calls the unchanged `ask_ai()` through `ClaudeProvider`. The official Anthropic Messages API receives the existing `LearningResult` JSON schema, tutor instructions, bounded conversation history and learning context. Only a complete valid result is committed to history/progress. Questions, hints and confusion retain the existing safeguards against false assessment.

Claude disables both OpenAI providers for that launch, regardless of their environment flags. No scripted fallback, provider fallback or automatic paid retries. The browser receives replies, safe errors and numeric usage only; credentials and model configuration remain server-side. Static demo mode stays separate.

Installed: `anthropic==1.15.0`, only in `NMI/.venv`. Public official documentation confirms **`claude-sonnet-5-5`** as an active Sonnet model. This is a recommended candidate, not an account-availability claim. An explicit owner command checks model metadata without inference. The adapter also checks the exact ID, lifecycle and structured-output capability before every Messages POST; it never substitutes a model automatically.

Official sources checked 16 October 2026:

- [Sonnet 5.5 ID, capabilities and pricing](https://platform.claude.com/docs/en/models/sonnet-5-5/overview)
- [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Python SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python)

## Safe launch now: no credentials or inference

First stop the old NMI server with Ctrl+C in its own terminal. Do not kill unrelated processes. In a new PowerShell terminal:

```powershell
Set-Location 'C:\Users\ahmad\OneDrive\Desktop\studdy app\NMI'
$env:NMI_AI_PROVIDER = 'claude'
$env:NMI_CLAUDE_MODEL = 'claude-sonnet-5-5'
$env:NMI_ENABLE_AI = '0'
$env:NMI_ENABLE_ANTHROPIC_PAID = '0'
$env:NMI_ENABLE_PAID_API = '0'
$env:NMI_ENABLE_CHATGPT_SIGNIN = '0'
.\.venv\Scripts\python.exe -B tools/run_claude.py --acceptance
```

Copy the entire private URL printed in **your terminal** into Chrome. Never share it. Its fragment is consumed and removed; a signed HttpOnly cookie is verified before the single browser session is claimed. The main chat shows Claude with inference disabled. Startup, opening the page and refreshing status make no provider request.

`--acceptance` creates a fresh fictional Grade 10 profile in a new ignored `.cache/claude-acceptance/<random-id>/synthetic.sqlite3`. Its allowance is one attempt after enabling. No existing records or earlier test folders are opened or deleted. The server binds loopback before opening data; a Windows lock prevents overlapping access to its store. Existing acceptance directories are refused.

## Owner-only account model check

Do not paste keys into chat, source files, command-line arguments or screenshots. After stopping the server, enter the owner's key through a hidden prompt in the same PowerShell process:

```powershell
$nmiClaudeSecret = Read-Host 'Anthropic API key (hidden)' -AsSecureString
$env:ANTHROPIC_API_KEY = [System.Net.NetworkCredential]::new('', $nmiClaudeSecret).Password
Remove-Variable nmiClaudeSecret
.\.venv\Scripts\python.exe -B tools/run_claude.py --check-model
```

This explicit command contacts the Models endpoint only. It prints the non-secret model ID or a safe error code, without generating an answer. Successful metadata verification does not guarantee sufficient credits, organization policy or service capacity. Do not replace the model without verifying its exact ID and structured-output support.

The key is accessed only by an explicit account check or enabled request. The old OpenAI key is never used. Process environment variables are not a credential vault; keep this terminal private and close it after testing. Custom Anthropic auth-token/header overrides are rejected. Proxy inheritance, redirects and SDK tracing are disabled; HTTPS certificate verification remains enabled. A network requiring a proxy is not supported by this first adapter.

## First paid request: separate approval required

**Do not run this section until the owner separately authorizes the first paid request.** Implementation approval did not authorize inference.

After a successful metadata check and approval, keep the server-side key in that terminal:

```powershell
$env:NMI_ENABLE_AI = '1'
$env:NMI_ENABLE_ANTHROPIC_PAID = '1'
$env:NMI_ENABLE_PAID_API = '0'
$env:NMI_ENABLE_CHATGPT_SIGNIN = '0'
.\.venv\Scripts\python.exe -B tools/run_claude.py --acceptance
```

Open the new private URL in Chrome. Confirm Claude is displayed, choose Arabic or English, check the Anthropic paid-request consent, and send **one synthetic question** in the main composer. Any normal question is supported; no question is hardcoded. Stop after a failure or uncertain outcome. “Check saved request status” reads the local receipt without resending. Failed attempts consume the allowance. Restarting resets the allowance, so do not restart to bypass the first-test restriction.

After testing, stop with Ctrl+C and clear the process key:

```powershell
$env:NMI_ENABLE_AI = '0'
$env:NMI_ENABLE_ANTHROPIC_PAID = '0'
Remove-Item Env:\ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
```

When normal conversations are approved, omit `--acceptance` and choose an explicit budget, for example `--max-calls 20`. This preserves `.local-data/claude-conversations/tutor.sqlite3` across restarts, without importing earlier ChatGPT/CLI records. The generic `local_web.py` also supports the Claude environment settings but retains its existing `.local-data/tutor.sqlite3`; use the dedicated launcher for isolated testing.

## Limits and failure behavior

- Both `NMI_ENABLE_AI=1` and `NMI_ENABLE_ANTHROPIC_PAID=1` are required; both default off. `NMI_CLAUDE_MODEL` has no implicit default. The dedicated launcher always selects Claude and disables OpenAI.
- Exactly one Messages POST per submitted request ID; zero SDK retries. Duplicate receipts return the saved reply/usage without another inference. Changed payloads under the same ID are rejected.
- Connect/write/pool timeouts: 5/10/5 seconds. Read inactivity: 30 seconds. Total model lookup plus stream: 90 seconds. A stalled stream is cancelled and closed. Browser timeout: 150 seconds, then read-only reconciliation. Cancellation cannot guarantee reversal of provider charges.
- Maximum output: 1,800 tokens. Existing limits: 4,000 message characters, 20 recent messages of context, 200 stored conversation messages and six requests/minute. No external tools or uploads. Sonnet 5.5 uses low effort and `between_tools` to avoid up-front thinking for text-only tutoring.
- Streaming is server-side, buffered until a complete valid `LearningResult` exists. Browser: loading, then complete reply; no partial JSON. Truncation, refusal, invalid fields and interruptions do not save a failed exchange or learning attempt. A numeric usage ledger can still be saved because a failed paid response may consume tokens.
- Usage includes reported input/output/cache-read/cache-write tokens. Partial reports are labelled; unavailable counts remain unknown. Usage is stored with receipts and displayed bilingually. Counts are not a dollar estimate or billing cap.
- `store=false` is an OpenAI option and is not sent to Anthropic's Messages API. No zero-retention promise is made. Only the required bounded tutoring context is sent after consent. Exception details, payloads and credentials are not logged; SDK tracing is off.
- Local single-tester prototype only: no public authentication, multi-student access or encryption claim. Existing privacy review is required before real minors' data or public use. No curricula, assessment policy, rules, logo or design were changed.
- Account model access, credit balance, live service behavior and Arabic teaching quality remain untested. Synthetic tests demonstrate software integration, not actual model quality.

## Offline checks

```powershell
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests/local -q
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests/offline -q
.\.venv\Scripts\python.exe -B -m pip check
.\.venv\Scripts\python.exe -X utf8 -B tools/validate_setup.py
node --test tests/frontend-state.test.cjs
node tools/run_frontend_tests.cjs --config=playwright.claude.config.cjs
node tools/run_frontend_tests.cjs --config=playwright.phase1.config.cjs
```

Claude browser tests use port 8771, synthetic SQLite in `.cache`, and the installed SDK over mocked HTTP/SSE. Remote sockets and external browser requests are denied. Windows asyncio's internal loopback wakeup sockets are permitted. No real account, browser profile, key or student file is used. Test results are recorded in [CLAUDE_VERIFICATION.md](CLAUDE_VERIFICATION.md).
