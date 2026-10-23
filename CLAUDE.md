# NMI

NMI (Next Mastery Intelligence) is an AI tutor for Grades 9–12, Arabic/English UI, Math/Physics/Chemistry only for scoring. Claude (Anthropic) is the only AI provider.

## How it works
- `python tools/run_claude.py` starts the loopback-only Flask app (127.0.0.1:8766). It prints a private link; open it in one Chrome profile. `--acceptance` = fresh fictional data, one request. `--check-model` = model metadata check, no inference.
- Inference is OFF unless both `NMI_ENABLE_AI=1` and `NMI_ENABLE_ANTHROPIC_PAID=1` are set. Model comes only from `NMI_CLAUDE_MODEL` (owner-set). Key comes from `ANTHROPIC_API_KEY`.
- Frontend: static HTML/CSS/vanilla JS in `preview/`. `serve_preview.py` (port 8765) is a synthetic demo; `live.js` is the Flask-only controller.
- Run from the project root with `.venv`. Setup: `.venv\Scripts\python.exe -m pip install -r requirements.txt`.

## Important files
- `ai_test.py` `ask_ai()` builds the tutor prompt (`tutor_rules.txt`, curriculum, progress, history) and parses a `LearningResult`.
- `claude_provider.py` Messages API adapter (streaming, structured output, safe error codes).
- `local_web.py` Flask routes, session/CSRF, receipts. `local_store.py` SQLite store in `.local-data/`.
- `curriculum.py`, `progress.py`, `chat_history.py`, `student_profile.py`, `main.py` (CLI, singleton JSON).
- Specs: `NMI_PRODUCT_SPEC.md` (requirements), `DESIGN.md` (visual rules).

## Tests (run from project root)
- `.venv\Scripts\python.exe -B -m unittest discover -s tests/offline`
- `.venv\Scripts\python.exe -B -m unittest discover -s tests/local`
- `node tools/run_frontend_tests.cjs` and `node tools/run_frontend_tests.cjs -c playwright.claude.config.cjs`
- Tutor evals (owner-run, paid): `tools/run_evals.py`, cases in `tests/evals/tutor_cases.json`; see `tests/evals/README.md`. Never run it without the owner's approval.
- Tests use mocked SDK transport and temp data under `.cache`; no network, no real keys, no student data.

## Rules that must not break
- Never read, print, copy or upload API keys or credentials. Never touch `.local-data` or real student data.
- Never run a paid request or `--check-model` without the owner's approval. No automatic retry, no provider fallback, no uncertain-request resend.
- Bind to 127.0.0.1 only. Single claimed browser session with CSRF. Not multi-student auth or public-deployment ready.
- Do not silently overwrite corrupted data; preserve it and report.
- V1 targets desktop widths >= 1280px; no mobile layouts. Arabic and English only (RTL/LTR).
- Do not edit `tutor_rules.txt` or add features beyond the task.
- No git push, purchases or uploads.

## قواعد التعديل
- التصميم مقصود يكون أبيض وأسود وبسيط. لا تغيّره ولا تحسّنه ولا تضيف ألوان.
- ممنوع تلمس ملفات css أو tokens.css أو الشكل، إلا إذا طلبت تغيير تصميم بالاسم.
- عدّل بس الإشي المطلوب بالضبط. ممنوع تعيد بناء أي صفحة.
- قبل التعديل، قلي شو الملفات اللي رح تلمسها.

## الاتجاه الحالي
- الطلاب ما رح يتركوا ChatGPT وClaude وGemini. فالمنتج الجديد اسمه "عدّة NMI": صفحة بتجهّز للطالب برومبت فيه منهاجه ونمط البجروت وقواعد التدريس، والطالب بيستعمله بالتطبيق اللي عنده.
- المنتج الرئيسي هو `kit/` (صفحة ثابتة: `index.html`، `prompt.js`، `app.js`، `data.json`). `data.json` بيتبني من `curriculum/` بـ `python tools/build_kit.py`، وما بيتعدّل بإيد. `python tools/build_kit.py --check` بيفحص إنه محدّث.
- الموعد النهائي: 30/10/2026.
- الموقع الحالي (`local_web.py`، `ai_test.py`، الـ evals، `preview/`) بيضل "مختبر" لتجربة قواعد المدرّس. ما تمسحه وما تغيّره إلا إذا انطلب.
- مصدر المحتوى: `curriculum/<مادة>/grade<N>/<N>units.md`، و`curriculum/<مادة>/bagrut_patterns.md`، وبنك الأمثلة `curriculum/<مادة>/grade<N>/examples/<N>units.md` (كل مثال بيتفحص بـ sympy بـ `tests/kit/example_solutions.py`). مادة جديدة بتنضاف بمجلد بدون كود. مستوى ناقصه أمثلة بينعلّم "تجريبي".
- اختبارات العدّة: `python -B -m unittest discover -s tests/offline`، و`node --test tests/kit/prompt.test.cjs`، و`node tools/run_frontend_tests.cjs -c playwright.kit.config.cjs`. النشر على GitHub Pages: `docs/KIT.md`.
