# Tutor evals

`tutor_cases.json` has 25 Arabic cases for Grade 10 math (16 for 3 units, 4 for 4 units, 5 for 5 units). Each case has `profile`, `conversation` (ends with the student's message), `intent`, `expected_behavior`, `math` (reference answer and `must_withhold` or `must_state`, or null) and `expect_attempt` (should the tutor record a learning attempt, and was it correct). All are synthetic, not student records. The topic placement (for example derivatives and logarithms in Grade 11) follows the owner's brief and must be checked against the curriculum files when they exist.

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
.\.venv\Scripts\python.exe -B tools/run_evals.py --max-cases 5
.\.venv\Scripts\python.exe -B tools/run_evals.py --only m10-sign-01 m10-conf-01
```

`--max-cases` defaults to 5 and picks one case per category in turn. `--only` overrides it. There are no retries; a key, billing or model error stops the run. The report is written to `tests/evals/report.md`.

Offline tests with fake models: `tests/offline/test_run_evals.py` and `tests/local/test_run_evals_claude.py`.
