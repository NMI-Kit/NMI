---
name: nmi-tutor-testing
description: Evaluate NMI teaching intent, Arabic typo interpretation, hints, confusion, assessment validity, and adaptation using synthetic offline tutor cases.
---

Use [the evaluation guide](../../../tests/evals/README.md) and `tests/evals/tutor_cases.json`. This owns pedagogical semantics; persistence/API fault testing belongs to nmi-reliability-testing.

- Classify the student's current intent using exercise context: question, answer, hint request, confusion, or ambiguous. A question, hint or expression of confusion is not an incorrect attempt. A number alone without an active exercise may need clarification.
- Treat قيزياء as a possible physics spelling error, not proof of identity, subject or skill. Ask a clarifying question when context is insufficient. Preserve the student's original wording.
- An assessed attempt requires supported subject/topic/skill identifiers and actual boolean correct/hint_used. Do not fill missing fields from guesses; do not invent mistake types or grades.
- Review one concept at a time, concept before formula, progressive hints, and adaptation to demonstrated prior mistakes. Compare synthetic learner A and B with different histories without mixing records.
- Mock OpenAI before importing ai_test. Run `python -B -m unittest discover -s tests/offline -v` with NMI's venv. This verifies plumbing only; a prewritten mock does not prove the real model understands Arabic or adapts.
- For semantic evaluation, record case ID, observed reply, rubric evidence and pass/fail/unevaluated. No live API evaluation under Skills setup. Never modify tutor_rules.txt or model behavior as a side effect of testing.

