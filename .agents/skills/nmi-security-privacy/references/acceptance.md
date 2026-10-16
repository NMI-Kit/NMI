# Synthetic security acceptance

Use two fabricated students and a third unauthenticated session. A logs in and requests B's profile, history, progress, export and attempt creation by altering route/query/body IDs: require denial and unchanged B data. Repeat with a non-existent ID without revealing whether B exists. Verify per-request state and concurrent calls cannot inherit another identity. These are future route tests; no such routes exist today.

Submit HTML/script-like text, oversized messages, unknown locale, wrong JSON types and path traversal strings. Require safe rendering, explicit rejection where appropriate and no data corruption. Put a synthetic sentinel in mocked credentials and student messages; capture logs and verify the sentinel is absent. No actual credential access is necessary.

Test session expiry, CSRF rejection, cookie flags, disallowed origins and rate-limit behavior once Flask exists. Record missing implementation as blocked, not passed.

