# NMI: ChatGPT conversations on your local device

Updated 15 October 2026. **Normal tutoring has no fixed-question restriction.** Arabic and English questions, follow-ups and requests for another explanation use the actual provider through `ask_ai()`. There is no scripted reply fallback on Flask. Real account authorization and live model/schema compatibility have not yet been verified; passing mocks do not establish those facts.

## Start conversation mode

The previously running acceptance server must be restarted to load the updated Python code. In its owner terminal type `quit` (or press Ctrl+C). Keep all existing data. Then, from an interactive PowerShell terminal:

```powershell
Set-Location 'C:\Users\ahmad\OneDrive\Desktop\studdy app\NMI'
.\.venv\Scripts\python.exe -B .\tools\run_chatgpt.py --max-calls 20
```

This starts only on `127.0.0.1:8766`, with ChatGPT sign-in ON, inference OFF and paid API billing OFF. It does not read an API key, honor paid-API environment flags, start OAuth or send inference automatically. Another listener is never replaced by this launcher.

Unlike the acceptance harness, conversation mode reuses its own ignored `.local-data/chatgpt-conversations/tutor.sqlite3` across restarts. It does not import or overwrite CLI JSON, the previous website database, or earlier synthetic acceptance records. A per-store Windows process lock prevents a second launcher from opening this same single-user database. Tokens remain in memory; client/account registration metadata stays in that directory's `registration.json`. Do not open or share it.

Keep the terminal open. Copy its complete private URL into one Chrome profile. Do not share the URL or include it in screenshots. The browser removes its fragment after reading it. Open **Tutor connection** to reach Settings. Save the local country/grade profile if this new store asks for it. Existing saved profiles cannot be silently reassigned.

## Authorize personally and choose the model in the terminal

1. Confirm that the local session is unlocked; tutoring is initially disabled.
2. Click **Continue with ChatGPT** and personally sign in on the official authorization page. Review the requested plan permission. The agent must not enter a password or approve access for you.
3. Return to NMI. In the owner terminal type `status`, then `models`. This retrieves the account-authorized catalog, not an inference reply. Tokens are not printed.
4. Choose only an exact model slug returned for this account. Enter:

```text
enable AUTHORIZED_MODEL_SLUG
```

5. In NMI, click **Refresh connection status**, review and check the ChatGPT plan consent box, and send your own Arabic or English question in the main chat. Continue with follow-ups in the same composer.

Enabling rechecks the account's model authorization and permits the configured number of attempts. It does not send a question itself. No model picker or HTTP activation endpoint is exposed to students. Catalog availability does not by itself prove support for NMI's structured `LearningResult`; that remains part of the first live test.

Examples are not an allowlist: a mathematics question, a biology question, a change of topic, `I don't understand`, or an Arabic request for another explanation are all accepted. Use the appropriate message type when explicitly submitting an assessed exercise answer. A question, hint or confusion is never scored merely because the model guesses assessment fields.

## Conversation context and persistence

Each request includes the student's current message, recent saved conversation, grade/country/language, existing learning attempts and the unchanged tutor rules. Supplemental web guidance asks the model to infer the likely subject/topic and immediate learning need cautiously, understand Arabic dialect/spelling mistakes, follow topic changes, and use a different analogy or smaller example for confusion.

This is contextual model reasoning, not a deterministic keyword router or a new official student score. No separate permanent subject/learning-style classification is created. Unsupported official curricula and guessed strengths, weaknesses or mastery must not be invented.

A completed valid result saves the user message, tutor reply and any allowed assessment atomically. A failed, refused, invalid or interrupted response adds neither a failed exchange nor a learning attempt. Prior data remain intact. Refreshing the browser or restarting conversation mode retains this launcher's history; restarting requires a new private session and personal OAuth authorization because tokens are not persisted.

The `status` terminal command prints only safe connection configuration and saved message/attempt/receipt counts. It does not display conversations or credentials. `quit` stops the process and preserves records; it does not claim remote revocation.

## Optional isolated acceptance mode

For an agent-assisted first real test, use a fresh fictional profile and exactly one attempt:

```powershell
.\.venv\Scripts\python.exe -B .\tools\run_chatgpt.py --acceptance
```

`tools/run_chatgpt_test.py` remains a compatibility shortcut to this mode. It stores records under a new `.cache/live-acceptance/<run>/` directory and uses separate synthetic-test registration metadata. **Any normal Arabic or English question is accepted; no exact text is enforced.** `enable` and the older `arm` command both work. A failed attempt consumes the one-request allowance too. Do not restart to bypass a failed acceptance attempt. The agent must stop after the separately approved live attempt and report its result before another.

## Limits and error behavior

- Conversation mode defaults to 20 attempted inference requests per launch. The owner can choose `--max-calls 1` through `--max-calls 100`; this is a local usage cap, not a restriction on subject or wording. Failed attempts consume the cap. It cannot be silently reset from the browser or re-enabled in the same process.
- Existing safeguards remain: six requests per minute, 4,000 characters per student message, one saved conversation with up to 200 messages, and up to 100 attempts. The provider receives the last 20 saved messages and recent progress. Longer-term memory and multiple real conversations are not implemented yet.
- The provider uses official structured Responses streaming with `store=false`, `stream=true`, no automatic retry and no paid API fallback. It buffers a complete valid response before committing or displaying it.
- Browser chat waiting ends after 150 seconds, connection actions after 60 seconds and ordinary reads after 15 seconds. A browser timeout does not cancel or refund provider usage. **Check saved request status** only reads a receipt; it never resends inference. Do not resend when the outcome is uncertain.
- OAuth/account/model/usage errors are shown explicitly. A server failure cannot become a demo response. The static port-8765 preview remains a separate labeled demo.
- This is a local single-user prototype, not public authentication or multi-student hosting. Local files remain in the existing OneDrive workspace, whose OS sync is outside the app's control.

## Unlock troubleshooting

Use the current launch's full private URL with `127.0.0.1:8766`, not `localhost`, port 8765 or a previous launch's link. Allow site cookies. A cookie round trip occurs before claiming the owner session. Cookies are signed, HttpOnly and SameSite Strict with a port-specific name.

If the fragment remains visible, current `live.js` has not successfully processed it: reload and verify the server/assets. If a completed claim loses its cookie, a second browser remains intentionally denied. Stop and restart the server for a new session rather than disabling authentication. Conversation mode retains the same local history on restart.

`python -B local_web.py` is the older environment-configured entry point with a one-request default and a different database. Use `tools/run_chatgpt.py` for normal ChatGPT conversations; do not use historical paid-API launch instructions to solve ChatGPT access problems.

## Verification and live boundary

See [CONVERSATION_MODE_VERIFICATION.md](CONVERSATION_MODE_VERIFICATION.md) for this update and [PHASE1_VERIFICATION.md](PHASE1_VERIFICATION.md) for earlier unlock/main-chat repairs. Offline tests use isolated synthetic data, mocked OAuth and mocked streaming responses; browser tests run in installed Chrome without external provider traffic.

The official [models and inference requirements](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference) and [preview limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations) govern actual account access. The app cannot guarantee plan eligibility or model/schema compatibility before a successful live test. No real sign-in, model retrieval or inference was performed as part of removing the fixed-question restriction.
