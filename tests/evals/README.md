# Tutor evals

`tutor_cases.json` has 60 Arabic math cases: 25 basic Grade 10 cases (17 for 3 units, 4 for 4 units, 4 for 5 units), 27 hard cases, 3 conversation cases and 5 mode cases (see below). Each case has `profile`, `conversation` (ends with the student's message), `intent`, `expected_behavior`, `math` (reference answer and `must_withhold` or `must_state`, or null) and `expect_attempt` (should the tutor record a learning attempt, and was it correct). All are synthetic, not student records. The topic placement (for example derivatives and logarithms in Grade 11) follows the owner's brief and must be checked against the curriculum files when they exist.

## Hard cases (`tier: "hard"`)

27 cases, 3 for each grade (10, 11, 12) x units (3, 4, 5), ids `h<grade>u<units>-<n>`. Each has a `topic` (an m-ID that exists in that level's file under `curriculum/math/`) and `subject: "math"` in the profile. Per level there is one of each kind:

- `hard_multistep`: a Bagrut-style problem where the student's work goes wrong in one middle step.
- `hard_why`: a deep "why" question about a concept (no attempt should be recorded).
- `hard_trap`: a trap (two roots and a domain, an ambiguous case, a hole instead of an asymptote, a tangent, a negative ratio).

The correct answer of every hard case is computed independently with sympy in `hard_solutions.py` (`SOLUTIONS["h11u4-3"]()`). The offline test fails if `math.expected` differs from that result, if a recorded fact is false (for example the student's wrong step is not actually wrong), or if the conversation already contains the withheld answer. `h12u4-3` has no numeric answer (the correct result is that there is no minimum), so its facts are checked but `math` is null.

## Mode cases (`tier: "mode"`) and the judge

The tutor works in one of three modes, chosen by the model from the student's message in the same request (no extra call) and returned in the `mode` field: `explain` (a direct answer of about 150 words in light Markdown: what the topic is in the first sentence, the formula on its own line with one line per symbol, ONE solved example with numbered steps, ONE easy question; no headings, no topic ids, no "file", no Bagrut unless asked), `practice` (short, no answer, one question) and `plan` (a weekly plan from the curriculum file with topic ids and the exam form number).

Five cases at Grade 10, 3 units: four explain cases ("مش فاهم الدالة التربيعية", "مش فاهم الدالة الخطية", "شو يعني ميل ولشو منستعمله", "شو يعني رقم ثابت وشو هو y") and one plan case ("بدي خطة للبجروت"). Each carries the mode it expects and code checks:

- `mode`: the expected mode. The mode the model chose is read from the provider (`last_result`); a different mode fails the case (`wrong_mode`). A client that does not report its mode is not held against the tutor.
- `must_mention`: one spec or a list of specs `{"any_of": [...], "at_least": N}`. Explain cases need bold (`**`), the word "مثال" and, where there is a formula, a `$$` line (`missing_parts`). The plan case needs 6 topic ids, an exam form number and the word "week".
- `max_words`: 200 for explain (about 150 words plus Markdown signs); more fails the case (`too_long`).
- `forbidden_substrings`: plain text that must not appear, in any prefixed form. Explain cases forbid `m10-`, `ملف` (so also "الملف") and `بجروت` (so also "البجروت", "للبجروت"). The plan case has none, because ids, exam numbers and the Bagrut are what a plan is made of.

In every case and every mode the words "الملف", "ملف المنهاج" and "ملفات" are forbidden (`ALWAYS_FORBIDDEN` in `run_evals.py`, reported as `forbidden_phrase`): the student never hears about files. A plan may still name topic ids and the exam form number.

The judge is told `<mode_expected>` and the mode the tutor chose. For `explain` it checks the direct shape above and penalises an introduction or story, several headings, a long reply, a second example, ids, "file" and an unasked Bagrut; it does not penalise a short reply. It also judges correctness, dialect and whether the tutor explained in a different way when the student still did not understand.

## Bagrut practice cases (`tier: "bagrut"`)

A fourth mode, `bagrut`, answers "بدي أتدرّب على سؤال بجروت": the tutor writes a NEW question (never a real exam question) on a topic of the student's curriculum, following the "How the tutor writes a Bagrut practice question" section of `curriculum/math/bagrut_patterns.md`, which is loaded for every math student in the cached part of the prompt, after the curriculum. It gives the story and section أ only, waits, corrects the solution, and gives the next section.

Two cases at Grade 10, 3 units: `mode-bagrut-start-01` (the first reply has the story and "القسم أ" and nothing of ب, ج, د; no answer) and `mode-bagrut-next-01` (the student sends a right solution to section أ; the tutor confirms it, gives "القسم ب" only, and does not solve it: the answer, 4 months and 280 ₪, is computed by sympy in `hard_solutions.BAGRUT_SOLUTIONS`). `forbidden_sections` lists the section labels that must not appear yet (`extra_sections`); `must_mention` requires the label that must appear.

## Conversation cases (`tier: "conversation"`)

Three cases taken from the owner's own session with the website (ids `conv-...`): a student who writes Palestinian Arabic (the tutor must answer in that dialect, not Egyptian), a 3-unit student whose target is 5 units and who asks what to learn (the tutor must give a plan from `5units.md`), and a question about the quadratic function (the example must agree with the shape it describes: y = x² opens upward, y = −x² downward; the sympy facts are in `hard_solutions.CONVERSATION_SOLUTIONS`).

Two optional fields are checked by code, not by the judge:

- `forbidden_phrases`: whole words the reply must not contain (for example Egyptian words, or a claim that no curriculum is loaded). A hit fails the case (`forbidden_phrase`).
- `must_mention`: `{"any_of": [...], "at_least": N}`; the reply must name at least N of these topic words (`missing_plan`).

A profile may carry `target_units`; the runner passes it to `ask_ai`, which adds the target level's file to the cached part of the prompt.

`legacy_cases.json` keeps the earlier 22 unevaluated behavior specifications unchanged. `tools/run_evals.py` does not use it.

## How a case is scored

1. The runner calls the real `ask_ai` (`web_policy=True`, the same path as the website) with the case conversation in memory. It never touches `.local-data`, SQLite or the CLI JSON files.
2. Code checks the math with sympy: false arithmetic equations in the reply, a leaked final answer (`must_withhold`), or a missing correct answer (`must_state`). Equations that only quote the conversation are ignored. A written form that is still a step (`4√3 + 2√3`) is not counted as stating `6√3`.
3. Code checks that the learning attempt was recorded (or not) as `expect_attempt` says.
4. A Claude judge scores the reply 0-10 against `tutor_rules.txt` and `expected_behavior`, with a reason and weakness tags. It is told not to check arithmetic.

A case passes with a judge score of 7 or more, sound math, and a correct attempt record. Known limit: the math check reads plain text and simple LaTeX, so unusual notation is skipped, not failed.

## Running (paid: about 2 requests per case)

Both inference gates are required; the model and key come from the environment and are never printed.

```powershell
$env:NMI_ENABLE_AI = "1"
$env:NMI_ENABLE_ANTHROPIC_PAID = "1"
$env:NMI_CLAUDE_MODEL = "<tutor model id>"
$env:NMI_EVAL_JUDGE_MODEL = "<judge model id>"   # optional, defaults to the tutor model
$env:NMI_CLAUDE_EFFORT = "medium"                  # optional: low, medium or high; default medium (also for the website)
.\.venv\Scripts\python.exe -B tools/run_evals.py --max-cases 5
.\.venv\Scripts\python.exe -B tools/run_evals.py --only m10-sign-01 m10-conf-01
.\.venv\Scripts\python.exe -B tools/run_evals.py --grade 11 --units 4     # one level: all its cases (3 cases, 6 requests)
```

`--max-cases` defaults to 5 and picks one case per category in turn. `--grade` (10, 11, 12) and `--units` (3, 4, 5) keep only that level and then run every matching case unless `--max-cases` is given. `--only` overrides all of them. Grade 11 and 12 levels have 3 cases each (6 requests); grade 10 levels also include the 25 basic cases (3 units: 20 cases, 40 requests; 4 and 5 units: 7 cases, 14 requests each). The whole file is 52 cases, about 104 requests.

The report starts with a table per grade and units (average, weakest case, and why it was weak), then the per-case table. There are no retries; a key, billing or model error stops the run. The report is written to `tests/evals/report.md`.

Offline tests with fake models: `tests/offline/test_run_evals.py` and `tests/local/test_run_evals_claude.py`.
