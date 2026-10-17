---
name: nmi-reliability-testing
description: Test NMI Python and future Flask failure handling, malformed storage, mocked API failures, retry deduplication, and consistency between attempts and conversations.
---

Own fault injection and persistence invariants. nmi-tutor-testing owns teaching semantics; nmi-security-privacy owns access policy.

- Start with `tests/offline/test_backend_contracts.py`. Use NMI's venv with -B, fresh temporary data under NMI/.cache, a replaced OpenAI module before ai_test import, and a network-denial guard. Never run main.py against real files.
- Verify new/returning onboarding, no history/progress writes on invalid parsed output or invalid assessment, and exactly one append for each accepted successful request.
- Inject missing, truncated, corrupt, wrong-shaped and wrong-typed JSON; timeouts, connection/rate-limit/server errors; and disk failures between progress/history writes. Preserve earlier valid data. Check graceful localized failure contracts when implemented.
- A repeated request ID must not create a second attempt, while two distinct attempts with identical text must remain distinct. Test retries after partial failure and concurrent writes. Do not deduplicate merely by answer text.
- Future Flask tests use app.test_client with synthetic identities and a fake AI adapter, never a live server API key. Coordinate cross-student tests with security requirements.
- Separate passed tests, expected failures exposing existing gaps, skipped future capabilities and unexpected failures. Never mark expected failures as implemented protection. Fix only defects introduced by the authorized change; report unrelated learning defects.

