---
name: nmi-security-privacy
description: Review NMI credential protection, student ownership, input boundaries, record authorization, privacy-safe logging, and readiness before public deployment.
---

Own security requirements and threat review. nmi-backend-quality designs integration; nmi-reliability-testing exercises failures. Read [security acceptance cases](references/acceptance.md) when testing or preparing deployment.

- Keep API credentials on the server; never read or expose actual values during a review. Inspect references/configuration structurally. Never place secrets in HTML, JS bundles, repository files or logs.
- Derive student identity from verified server-side authentication, not a posted student_id, filename, locale or localStorage. Authorize every profile/history/progress read and write, including exports and list routes. Isolation must survive guessed IDs and simultaneous users.
- Validate types, lengths, enums and allowed locale at the boundary. Bound message/file sizes. Use parameterized database queries and safe path handling. Render student text as text or sanitized markup, never raw HTML.
- For future Flask sessions: evaluate secure/HttpOnly/SameSite cookies, CSRF for cookie-authenticated mutation, restrictive CORS, session expiry, rate limits and debug-off production configuration. Document choices without disabling protections for convenience.
- Logs should use non-sensitive event IDs and outcomes; exclude names, full messages, curriculum personal notes, tokens, headers and authentication state. Sanitize exception output and test redaction using synthetic markers.
- Before public deployment record implemented controls, failing cases, data retention/deletion policy and unresolved risks. Do not claim legal compliance or deploy from a review task.
- Current singleton JSON persistence cannot satisfy multi-student access control. Flag this explicitly; do not patch learning logic without an implementation task.

