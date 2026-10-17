---
name: nmi-backend-quality
description: Plan or review NMI Python module contracts and future Flask integration while preserving the existing tutor architecture and data formats.
---

Inspect main.py -> student_profile/ai_test -> curriculum/learning_result/progress/chat_history. subject_router.py is a separate keyword helper; do not assume ask_ai calls it. Flask is not currently installed or implemented.

- Keep HTTP request parsing, authentication and response mapping outside learning functions. Do not import a client-initializing module just to inspect schemas or start a static preview.
- Specify function arguments, ownership context, data shapes, error contracts and compatibility before implementing a route. Preserve existing CLI behavior unless the task changes it.
- Plan migration from singleton JSON stores to a student-scoped repository with explicit transaction boundaries. Include import validation, backups, provenance and rollback; never migrate real data during a design task.
- Use nmi-security-privacy to define identity/authorization/logging requirements, nmi-curriculum-quality for curriculum contracts, and nmi-reliability-testing to verify fault behavior. Do not maintain competing checklists here.
- Report actual current versus proposed behavior. Missing Flask, ownership, transactions and idempotency are implementation gaps, not capabilities supplied by installing this skill.

