# Offline tutor evaluation cases

Current scope: 22 cases for enrolled Grades 9-12. The literal Arabic command "شوي" comes from the user's master specification; its scenario is synthetic. Other examples are synthetic and explicitly labeled, not attributed to actual students. Each case includes provenance, enrolled_grade and evaluation_status. All are currently unevaluated against a real tutor reply.

Added coverage includes subject changes, a missing earlier prerequisite, a grounded prerequisite answer, repeated prerequisite errors, one-concept pacing and return to the original task. A learner's enrolled grade never changes during remediation. Earlier skill support does not authorize unsupported official curriculum generation.

For each future candidate response record: case ID, model/prompt version if known, exact non-sensitive reply, observed intent/assessment, evidence for each rubric criterion, pass/fail and reviewer. Require zero questions/hints/confusion recorded as incorrect attempts, zero invented official requirements, zero cross-learner references, and grounded fields for every assessed answer. A passing mock UI or storage test provides no evidence for these semantic gates. Do not claim training or improvement from this dataset alone.

`tutor_cases.json` contains fabricated messages and exercise context. These are behavior specifications, not official curriculum content or real student records. IDs are test identifiers, not production curriculum IDs.

Use nmi-tutor-testing to review intent, explanation, hint progression and adaptation. The backend tests inject fixed LearningResult dictionaries to verify storage/validation contracts. They do NOT demonstrate real AI understanding of these messages. All semantic cases remain unevaluated until actual candidate replies are supplied for offline review or a separately authorized model evaluation is performed.

Rubric: correct intent; no assessment of questions/hints/confusion; grounded assessment fields only; one concept before formula; hint progression without immediately revealing an answer; typo tolerance with clarification when genuinely ambiguous; no invented curriculum or grades; adaptation justified by provided history; no leakage between synthetic learners. Record evidence per criterion, not merely an overall score.

Run backend contract tests from NMI with `.venv/Scripts/python.exe -B -m unittest discover -s tests/offline -v`. Known expected failures identify existing reliability gaps and must not be described as passed behavior. Flask, authentication, idempotency and true multi-student storage do not exist yet.

