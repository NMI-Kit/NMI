"""Offline contracts only: no provider is constructed and no network is used."""
import contextlib
import importlib
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
ai = importlib.import_module("ai_test")
history = importlib.import_module("chat_history")
progress = importlib.import_module("progress")
student = importlib.import_module("student_profile")
curriculum = importlib.import_module("curriculum")
main = importlib.import_module("main")


def result(attempt=False, correct=None, **overrides):
    value = dict(reply="Synthetic tutor reply", is_attempt=attempt, subject="physics" if attempt else None,
                 topic="motion" if attempt else None, skill="speed" if attempt else None,
                 correct=correct, hint_used=False if attempt else None, mistake_type=None)
    value.update(overrides)
    return value


class BackendContracts(unittest.TestCase):
    def setUp(self):
        cache = ROOT / ".cache/offline"
        cache.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=cache)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        for module, name, filename in [(history, "HISTORY_FILE", "history.json"),
                                        (progress, "PROGRESS_FILE", "progress.json"),
                                        (student, "STUDENT_FILE", "student.json")]:
            self.stack.enter_context(patch.object(module, name, self.base / filename))
        # Synthetic curriculum tree: curriculum/<subject>/grade<N>/<units>units.md
        self.curriculum_dir = self.base / "curriculum"
        folder = self.curriculum_dir / "math" / "grade10"
        folder.mkdir(parents=True)
        (folder / "3units.md").write_text("Synthetic 3 units fixture", encoding="utf-8")
        (folder / "4units.md").write_text("Synthetic 4 units fixture", encoding="utf-8")
        self.stack.enter_context(patch.object(curriculum, "CURRICULUM_DIR", self.curriculum_dir))
        self.stack.enter_context(patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")))
        self.stack.enter_context(patch.object(socket, "create_connection", side_effect=AssertionError("Network forbidden")))
        self.stack.enter_context(patch.object(ai, "client", SimpleNamespace(responses=SimpleNamespace(parse=Mock(return_value=SimpleNamespace(output_parsed=result()))))))

    def ask(self, parsed, language="English"):
        ai.client.responses.parse.return_value = SimpleNamespace(output_parsed=parsed)
        return ai.ask_ai("Synthetic Student", "7", "Testland", language, "Synthetic message")

    def seed(self):
        history.save_history([{"role": "assistant", "content": "Previous synthetic reply"}])
        progress.save_progress({"attempts": [result(True, True)]})
        return history.HISTORY_FILE.read_bytes(), progress.PROGRESS_FILE.read_bytes()

    def assert_preserved(self, before):
        self.assertEqual(before, (history.HISTORY_FILE.read_bytes(), progress.PROGRESS_FILE.read_bytes()))

    def test_missing_data_defaults(self):
        self.assertIsNone(student.load_student())
        self.assertEqual(history.load_history(), [])
        self.assertEqual(progress.load_progress(), {})

    def test_new_onboarding(self):
        with patch("builtins.input", side_effect=["Example", "7", "Testland", "Arabic", "", "Question"]), contextlib.redirect_stdout(io.StringIO()):
            main.main()
        self.assertEqual(student.load_student()["name"], "Example")
        self.assertEqual(len(history.load_history()), 2)
        ai.client.responses.parse.assert_called_once()

    def test_returning_student_preserved(self):
        student.save_student("Example", "7", "Testland", "English")
        before = student.STUDENT_FILE.read_bytes()
        with patch("builtins.input", return_value="Question"), contextlib.redirect_stdout(io.StringIO()) as output:
            main.main()
        self.assertIn("Welcome back, Example", output.getvalue())
        self.assertEqual(before, student.STUDENT_FILE.read_bytes())

    def test_question_no_attempt(self):
        before = self.seed()
        self.ask(result())
        self.assertEqual(before[1], progress.PROGRESS_FILE.read_bytes())
        self.assertEqual(len(history.load_history()), 3)

    def test_correct_attempt(self):
        self.ask(result(True, True))
        self.assertTrue(progress.load_progress()["attempts"][0]["correct"])
        self.assertEqual(progress.calculate_mastery("physics", "motion", "speed"), 100)
        self.assertEqual(len(history.load_history()), 2)

    def test_incorrect_attempt_with_mistake(self):
        self.ask(result(True, False, mistake_type="synthetic-inversion"))
        attempt = progress.load_progress()["attempts"][0]
        self.assertIs(attempt["correct"], False)
        self.assertEqual(attempt["mistake_type"], "synthetic-inversion")

    def test_missing_parsed_result_preserves_data_both_languages(self):
        for language, phrase in [("Arabic", "عذرًا"), ("English", "Sorry")]:
            with self.subTest(language=language):
                before = self.seed()
                self.assertIn(phrase, self.ask(None, language))
                self.assert_preserved(before)

    def test_invalid_attempt_fields_preserve_data(self):
        bad = [{"subject": None}, {"topic": " "}, {"skill": ""}, {"subject": 4},
               {"correct": None}, {"correct": "true"}, {"correct": 1},
               {"hint_used": None}, {"hint_used": "false"}, {"hint_used": 0}]
        for override in bad:
            with self.subTest(override=override):
                before = self.seed()
                self.assertIn("Sorry", self.ask(result(True, True, **override) if "correct" not in override else result(True, **override)))
                self.assert_preserved(before)

    def test_history_and_progress_round_trip(self):
        messages = [{"role": "user", "content": "سؤال تجريبي"}]
        history.save_history(messages)
        self.assertEqual(history.load_history(), messages)
        payload = {"attempts": [{"subject": "test", "correct": False}]}
        progress.save_progress(payload)
        self.assertEqual(progress.load_progress(), payload)

    def test_missing_curriculum_fallback(self):
        self.assertIn("Do not invent curriculum requirements", curriculum.get_curriculum("Testland", "7"))

    def test_final_check_is_the_last_section_of_the_instructions(self):
        for web_policy in (False, True):
            with self.subTest(web_policy=web_policy):
                ai.client.responses.parse.reset_mock()
                ai.ask_ai("Synthetic Student", "10", "Israel", "English", "Synthetic message", web_policy=web_policy, units=4)
                instructions = ai.client.responses.parse.call_args.kwargs["instructions"]
                self.assertTrue(instructions.endswith(ai.FINAL_CHECK))
                self.assertEqual(instructions.count("# FINAL CHECK"), 1)
                self.assertLess(instructions.index(ai.rules_for_subject("math")), instructions.index("# FINAL CHECK"))
        self.assertIn("exactly one question", ai.FINAL_CHECK)
        self.assertIn("delete every question except the last one", ai.FINAL_CHECK)
        self.assertIn("do not do the student's next step for them", ai.FINAL_CHECK)
        self.assertIn("factor, substitute or calculate", ai.FINAL_CHECK)
        self.assertIn("Do not write the corrected version of the student's wrong step", ai.FINAL_CHECK)
        self.assertIn("The question asks for one single thing", ai.FINAL_CHECK)
        self.assertIn("at most five sentences) and about one idea", ai.FINAL_CHECK)
        for part in ("In practice mode", "In explain mode", "In plan mode", "about 150 words, no headings and no introduction",
                     "The first sentence says what the topic is",
                     "ONE solved example with numbered steps", "numbers different from the student's own exercise",
                     "No topic ids", "Bagrut or exam unless the student asked", "exam form number", "no raw HTML", "between $$ and $$"):
            self.assertIn(part, ai.FINAL_CHECK)

    def test_only_the_current_subject_section_of_the_rules_is_sent(self):
        full = ai.tutor_rules
        math = ai.rules_for_subject("math")
        for heading in ("# GENERAL RULES", "# MATHEMATICS", "# LEARNING RESULT DATA", "TEACHING RULES", "NMI BEHAVIOR"):
            self.assertIn(heading, math)
        for heading in ("# PHYSICS", "# CHEMISTRY", "# ENGLISH", "# HISTORY"):
            self.assertNotIn(heading, math)
        self.assertLess(len(math), len(full) * 0.85)  # the other subjects are still left out
        self.assertEqual(ai.rules_for_subject("Mathematics"), math)
        self.assertEqual(ai.rules_for_subject("رياضيات"), math)
        # Nothing is rewritten: every kept line is a line of tutor_rules.txt, in the same order.
        position = 0
        for line in math.splitlines():
            position = full.index(line, position)
        physics = ai.rules_for_subject("physics")
        self.assertIn("# PHYSICS", physics)
        self.assertNotIn("# MATHEMATICS", physics)
        self.assertIn("# LEARNING RESULT DATA", physics)
        for unknown in ("", "music", None):
            self.assertEqual(ai.rules_for_subject(unknown), full)  # unknown subject: send everything
        self.assertEqual(ai.tutor_rules, (ROOT / "tutor_rules.txt").read_text(encoding="utf-8"))

    def test_stable_prefix_is_rules_then_curriculum_and_identical_between_requests(self):
        def send(message, name="Synthetic Student", units=4, **options):
            ai.client.responses.parse.reset_mock()
            ai.ask_ai(name, "10", "Israel", "English", message, units=units, **options)
            return ai.client.responses.parse.call_args.kwargs

        first = send("first question")
        history.save_history([{"role": "assistant", "content": "Previous synthetic reply"}])
        progress.save_progress({"attempts": [result(True, True)]})
        second = send("a different question", name="Another Name", web_policy=True, intent="answer")
        prefix = first["cache_prefix"]
        self.assertEqual(second["cache_prefix"], prefix)
        self.assertEqual(prefix, ai.rules_for_subject("math") + "\n\n# STUDENT CURRICULUM\n" + "Synthetic 4 units fixture")
        for call in (first, second):
            self.assertTrue(call["instructions"].startswith(prefix + "\n\n"))
            variable = call["instructions"][len(prefix) + 2:]
            self.assertTrue(variable.endswith(ai.FINAL_CHECK))
            self.assertIn("# STUDENT INFORMATION", variable)
            self.assertIn("# STUDENT PROGRESS", variable)
            for part in ("Name: ", "Preferred language", "Previous synthetic reply", "first question", "a different question"):
                self.assertNotIn(part, prefix)
        self.assertIn("LOCAL WEBSITE SAFETY", second["instructions"][len(prefix):])
        self.assertNotIn("LOCAL WEBSITE SAFETY", prefix)
        self.assertNotEqual(send("again", units=3)["cache_prefix"], prefix)  # another curriculum, another prefix

    def test_modes_formatting_and_dialect_are_in_the_cached_rules_once(self):
        ai.client.responses.parse.reset_mock()
        ai.ask_ai("Synthetic Student", "10", "Israel", "Arabic", "بدي أتعلم", units=4)
        call = ai.client.responses.parse.call_args.kwargs
        for heading in ("# TEACHING MODES", "# FORMATTING", "# LANGUAGE AND DIALECT"):
            self.assertEqual(call["cache_prefix"].count(heading), 1, heading)  # in the cached part, and only once
            self.assertNotIn(heading, call["instructions"][len(call["cache_prefix"]):])
        self.assertFalse(hasattr(ai, "DIALECT_RULE"))
        rules = ai.tutor_rules
        for part in ("EXPLAIN mode", "PRACTICE mode", "PLAN mode", '"mode" field', "in about 150 words", "No introduction, no story, no headings",
                     "The first sentence says what the topic is", "on a line of its own (between $$ and $$)", "one line for each",
                     "ONE solved example, step by step, with numbered steps", "ONE easy question for the student, at the end",
                     "**bold** for the key words and bullet points", "Never write topic", "unless the student asked about it",
                     "explain it in a different way", "exam form number", "m10-3-12", "between $$ and $$",
                     "Palestinian dialect", "هنبدأ", "كده", "إيه", "بالظبط", "unless the student writes in Egyptian"):
            self.assertIn(part, rules)
        for gone in ("## الفكرة ببساطة", "## المصطلحات", "## كيف بييجي بالبجروت", "about\n400 words", "two worked examples"):
            self.assertNotIn(gone, rules)
        # The three subject-independent sections are kept for every subject, and nothing existing was changed.
        for subject in ("math", "physics", "unknown"):
            self.assertIn("# TEACHING MODES", ai.rules_for_subject(subject))
        self.assertTrue(rules.startswith(rules.split("# TEACHING MODES")[0]))
        self.assertIn("- Ask one question at a time.", rules)
        self.assertIn("# LEARNING RESULT DATA", rules)

    def test_yabqa_is_in_the_dialect_rule_of_the_rules_file_with_its_replacement(self):
        rules = ai.tutor_rules
        dialect = rules[rules.index("# LANGUAGE AND DIALECT"):]
        egyptian = dialect[dialect.index("Never use Egyptian words ("):dialect.index("unless the student writes in Egyptian")]
        for word in ("هنبدأ", "كده", "إيه", "بالظبط", "عشان كده", "دلوقتي", "أوي", "إزاي", "يبقى"):
            self.assertIn(word, egyptian)
        self.assertIn('Do not use يبقى to mean "so" or "then"', dialect)
        self.assertIn("يعني", dialect)
        self.assertEqual(dialect.count("يبقى"), 3)  # the list, the rule and its example
        # the same words the evals forbid
        import json
        cases = json.loads((ROOT / "tests" / "evals" / "tutor_cases.json").read_text(encoding="utf-8"))
        for case in cases:
            if case.get("forbidden_phrases"):
                self.assertIn("يبقى", case["forbidden_phrases"], case["id"])
        # the dialect rule is sent in the cached part of every request
        ai.client.responses.parse.reset_mock()
        ai.ask_ai("Synthetic Student", "10", "Israel", "Arabic", "بدي أتعلم", units=4)
        self.assertIn("إزاي، يبقى)", ai.client.responses.parse.call_args.kwargs["cache_prefix"])

    def test_intent_label_is_only_a_hint_for_the_mode(self):
        ai.client.responses.parse.reset_mock()
        ai.ask_ai("Synthetic Student", "10", "Israel", "Arabic", "مش فاهم", units=4, web_policy=True, intent="confusion")
        variable = ai.client.responses.parse.call_args.kwargs["instructions"]
        self.assertIn("Student-selected intent: confusion", variable)
        self.assertIn("confusion usually means explain", variable)
        self.assertIn("the student's message decides", variable)

    def test_moving_up_a_level_sends_both_curriculum_files_in_the_cached_part(self):
        def send(**options):
            ai.client.responses.parse.reset_mock()
            ai.ask_ai("Synthetic Student", "10", "Israel", "Arabic", "شو لازم أتعلم؟", units=3, **options)
            return ai.client.responses.parse.call_args.kwargs

        plain = send()["cache_prefix"]
        self.assertEqual(plain, ai.rules_for_subject("math") + "\n\n# STUDENT CURRICULUM\nSynthetic 3 units fixture")
        call = send(target_units=4)
        prefix = call["cache_prefix"]
        self.assertTrue(prefix.startswith(plain))  # the current level file is unchanged and comes first
        self.assertIn("# TARGET LEVEL CURRICULUM (4 units)\nSynthetic 4 units fixture", prefix)
        self.assertIn(ai.LEVEL_TRANSITION.format(units=3, target=4), prefix)
        self.assertLess(prefix.index("Synthetic 3 units fixture"), prefix.index("Synthetic 4 units fixture"))
        for rule in ("cover the difference between them step by step", "topics that are in the target level file and not in the current level file",
                     "short ordered plan from the target file's topics", "Do not invent topics"):
            self.assertIn(rule, prefix)
        self.assertTrue(call["instructions"].startswith(prefix + "\n\n"))
        self.assertNotIn("TARGET LEVEL", call["instructions"][len(prefix):])  # nothing of it in the uncached part
        self.assertEqual(send(target_units=4)["cache_prefix"], prefix)  # identical between requests
        for ignored in (None, "", 3, "3", 5, 6):  # same level, or no such file in the fixture: no target section
            with self.subTest(target_units=ignored):
                self.assertEqual(send(target_units=ignored)["cache_prefix"], plain)

    def test_target_is_ignored_when_the_student_has_no_curriculum_file(self):
        ai.client.responses.parse.reset_mock()
        ai.ask_ai("Synthetic Student", "7", "Testland", "Arabic", "x", units=3, target_units=4)
        self.assertNotIn("TARGET LEVEL", ai.client.responses.parse.call_args.kwargs["cache_prefix"])

    def test_bagrut_patterns_are_loaded_after_the_curriculum_in_the_cached_part_for_every_math_student(self):
        def send(country="Israel", grade="10", subject="math", name="Synthetic Student", **options):
            ai.client.responses.parse.reset_mock()
            ai.ask_ai(name, grade, country, "Arabic", "بدي أتدرّب على سؤال بجروت", subject=subject, **options)
            return ai.client.responses.parse.call_args.kwargs

        base = ai.rules_for_subject("math") + "\n\n# STUDENT CURRICULUM\nSynthetic 4 units fixture"
        self.assertEqual(send(units=4)["cache_prefix"], base)  # no patterns file: nothing is added
        file = self.curriculum_dir / "math" / "bagrut_patterns.md"
        file.write_text("# أنماط\nشكل أسئلة البجروت\n", encoding="utf-8")
        call = send(units=4)
        prefix = call["cache_prefix"]
        self.assertEqual(prefix, base + "\n\n# BAGRUT QUESTION PATTERNS\n# أنماط\nشكل أسئلة البجروت")
        self.assertTrue(call["instructions"].startswith(prefix + "\n\n"))
        self.assertNotIn("BAGRUT QUESTION PATTERNS", call["instructions"][len(prefix):])
        # the same for every student of the subject, in every request
        history.save_history([{"role": "assistant", "content": "Previous synthetic reply"}])
        self.assertEqual(send(units=4, name="Another Name", web_policy=True, intent="answer")["cache_prefix"], prefix)
        # after the curriculum and, when the student moves up, after the target level and the transition rules
        moving = send(units=3, target_units=4)["cache_prefix"]
        self.assertLess(moving.index("Synthetic 3 units fixture"), moving.index("# TARGET LEVEL CURRICULUM"))
        self.assertLess(moving.index("# LEVEL TRANSITION"), moving.index("# BAGRUT QUESTION PATTERNS"))
        self.assertTrue(moving.endswith("شكل أسئلة البجروت"))
        # every math student gets it, even one without a curriculum file; other subjects have no patterns file
        self.assertIn("# BAGRUT QUESTION PATTERNS", send(country="Testland", grade="7", units=3)["cache_prefix"])
        self.assertNotIn("# BAGRUT QUESTION PATTERNS", send(subject="physics", units=4)["cache_prefix"])  # the heading; the rules only mention it
        self.assertIsNone(ai.bagrut_patterns("physics"))
        self.assertEqual(ai.bagrut_patterns("رياضيات"), "# أنماط\nشكل أسئلة البجروت")

    def test_the_real_patterns_file_is_part_of_the_cached_prefix_of_an_israeli_math_student(self):
        with patch.object(curriculum, "CURRICULUM_DIR", ROOT / "curriculum"):
            ai.client.responses.parse.reset_mock()
            ai.ask_ai("Synthetic Student", "10", "Israel", "Arabic", "بدي سؤال بجروت", units=3)
            prefix = ai.client.responses.parse.call_args.kwargs["cache_prefix"]
        patterns = (ROOT / "curriculum" / "math" / "bagrut_patterns.md").read_text(encoding="utf-8").strip()
        self.assertTrue(prefix.endswith("# BAGRUT QUESTION PATTERNS\n" + patterns))
        self.assertLess(prefix.index("# STUDENT CURRICULUM"), prefix.index("# BAGRUT QUESTION PATTERNS"))
        self.assertIn("رياضيات، الصف العاشر، 3 وحدات", prefix)
        for part in ("## كيف المدرّس يكتب سؤال تدريب بنمط البجروت", "بيعطي القسم الأول بس", "ما بينسخ أسئلة امتحانات حقيقية",
                     "35172 أو 35173", "35571 (60%)"):
            self.assertIn(part, prefix)

    def test_every_file_the_command_line_code_writes_is_ignored_by_git(self):
        lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        for name in ("chat_history.json", "answer_key.json", "progress.json", "student.json"):
            self.assertIn(name, lines)
        # the ignored names are the ones the code really writes, and no other module writes a data file
        constants = {"chat_history.py": ('HISTORY_FILE = BASE_DIR / "chat_history.json"', 'ANSWER_KEY_FILE = BASE_DIR / "answer_key.json"'),
                     "progress.py": ('PROGRESS_FILE = BASE_DIR / "progress.json"',),
                     "student_profile.py": ('STUDENT_FILE = BASE_DIR / "student.json"',)}
        for module, expected in constants.items():
            source = (ROOT / module).read_text(encoding="utf-8")
            for line in expected:
                self.assertIn(line, source, module)
        for folder in (".local-data/", ".cache/", "*.sqlite3", "*.sqlite3-*", ".env", "tests/evals/report*.md"):
            self.assertIn(folder, lines)  # the web server's database, test data and eval reports

    def test_no_curriculum_text_the_tutor_reads_says_file(self):
        # The tutor must not repeat "الملف", so the texts it reads do not use the word. SOURCES.md is for the teacher.
        root = ROOT / "curriculum"
        texts = sorted(root.glob("math/grade1[0-2]/[345]units.md")) + [root / "math" / "bagrut_patterns.md"]
        self.assertEqual(len(texts), 10)
        for path in texts:
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("ملف", content, path.name)  # also covers الملف, بهالملف, ملفات and ملف المنهاج
            self.assertNotIn("هالملف", content, path.name)
        self.assertIn("## تعليمات للمدرّس عن هذا الدليل", (root / "math/grade10/4units.md").read_text(encoding="utf-8"))
        self.assertIn("علّم بس المواضيع اللي بهالدليل.", (root / "math/grade10/4units.md").read_text(encoding="utf-8"))
        self.assertIn("الأخطاء الشائعة بهالدليل من خبرة تدريس عامة", (root / "math/grade12/5units.md").read_text(encoding="utf-8"))
        self.assertIn("هاد الدليل بيوصف **شكل** أسئلة البجروت.", (root / "math" / "bagrut_patterns.md").read_text(encoding="utf-8"))
        # version 3 of the patterns: one exam per level, with the 2025 table
        patterns = (root / "math" / "bagrut_patterns.md").read_text(encoding="utf-8")
        for part in ("(نسخة 3)", "035172 (صيف 2022)", "035472 (صيف 2022)", "3 وحدات، الصف العاشر: استمارة 35172",
                     "4 وحدات: استمارة 35472", "5 وحدات: استمارة 35571", "35172 أو 35173 (25%)", "35471 (65%)"):
            self.assertIn(part, patterns)
        self.assertIn("ملف", (root / "SOURCES.md").read_text(encoding="utf-8"))  # left as it was: it is for the teacher

    def test_bagrut_mode_is_in_the_rules_the_final_check_and_the_schema(self):
        rules = ai.tutor_rules
        self.assertEqual(rules.count("BAGRUT mode:"), 1)
        mode = " ".join(rules[rules.index("BAGRUT mode:"):rules.index("# FORMATTING")].split())  # one line, single spaces
        for part in ('("سؤال بجروت", "بدي أتدرّب"', "BAGRUT mode, not PRACTICE mode", "ONE NEW question", "BAGRUT QUESTION PATTERNS section",
                     "a short real-life story with all the numbers", "3 or 4 sections from easy to hard", "uses the result of the one before",
                     "Never copy a real exam question", 'exactly "القسم أ", "القسم ب"', "First reply: give the story and section أ only",
                     "Do not give any answer and do not show the next sections", "When the student sends a solution",
                     "do not give the next section", "give the next section only", "Do not invent more sections"):
            self.assertIn(part, mode)
        self.assertLess(rules.index("PLAN mode:"), rules.index("BAGRUT mode:"))
        self.assertIn("In bagrut mode", ai.FINAL_CHECK)
        self.assertIn("a NEW question (never a real exam question)", ai.FINAL_CHECK)
        self.assertIn("section \"القسم أ\" only", ai.FINAL_CHECK)
        self.assertIn("one small hint, no new section", ai.FINAL_CHECK)
        self.assertIn("# TEACHING MODES", ai.rules_for_subject("math"))  # kept for every subject

    def test_exam_form_numbers_follow_the_2025_table_of_the_patterns_file(self):
        root = ROOT / "curriculum"
        read = lambda name: (root / name).read_text(encoding="utf-8")
        table = read("math/bagrut_patterns.md")
        for row in ("35172 أو 35173", "35371 (35%)", "35372 (40%)", "35471 (65%)", "35472 (35%)", "35571 (60%)", "35572 (40%)"):
            self.assertIn(row, table)
        self.assertIn("35172 أو 35173", read("math/grade10/3units.md"))
        self.assertIn("35371", read("math/grade10/3units.md"))
        self.assertIn("35372", read("math/grade10/3units.md"))
        for name in ("math/grade10/5units.md", "math/grade11/5units.md", "math/grade12/5units.md"):
            text = read(name)
            self.assertIn("حسب جدول الوزارة 2025", text, name)
            self.assertIn("35571 (60", text, name)
            self.assertIn("35572 (40%)", text, name)
        self.assertIn("35571", read("math/grade11/5units.md").split("## الامتحان")[1])
        self.assertIn("35572", read("math/grade12/5units.md").split("## الامتحان")[1])
        # the old 5-unit numbers are gone from the level files and are only called old in the sources
        for path in root.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            if path.name in ("SOURCES.md", "bagrut_patterns.md", "NMI_KIT_TASK.md"):  # the last one is a task note, not curriculum
                continue
            for old in ("035581", "035582", "35581", "35582"):
                self.assertNotIn(old, text, f"{path.name}: {old}")
        sources = read("SOURCES.md")
        self.assertIn("35571 و35572) من جدول الوزارة 2025", sources)
        self.assertIn("35581 و35582 أرقام قديمة", sources)
        self.assertIn("35172 أو 35173", sources)
        self.assertNotIn("035581", sources)
        self.assertIn("| bagrut_patterns.md |", sources)

    def test_curriculum_by_units(self):
        self.assertEqual(curriculum.get_curriculum("Israel", "10", "math", 3), "Synthetic 3 units fixture")
        self.assertEqual(curriculum.get_curriculum("israel", 10, units="4"), "Synthetic 4 units fixture")
        self.assertEqual(curriculum.get_curriculum("Israel", "10", "math", 5).split(".")[0], curriculum.NOT_READY.split(".")[0])

    def test_curriculum_without_units_asks_student(self):
        for units in (None, "", "7"):
            with self.subTest(units=units):
                text = curriculum.get_curriculum("Israel", "10", "math", units)
                self.assertIn("level (units) is unknown", text)
                self.assertIn("3, 4 units", text)

    def test_curriculum_unknown_country_grade_subject(self):
        for args in [("Testland", "10"), ("Israel", "7"), ("Israel", "10", "physics")]:
            with self.subTest(args=args):
                self.assertIn("Do not invent curriculum requirements", curriculum.get_curriculum(*args, units=3))

    def test_ask_ai_passes_subject_and_units_to_curriculum(self):
        with patch.object(ai, "get_curriculum", wraps=curriculum.get_curriculum) as spy:
            ai.ask_ai("Synthetic Student", "10", "Israel", "English", "Synthetic message", units=4)
        spy.assert_called_once_with("Israel", "10", subject="math", units=4)
        self.assertIn("Synthetic 4 units fixture", ai.client.responses.parse.call_args.kwargs["instructions"])

    def test_student_units_optional(self):
        student.save_student("Example", "10", "Israel", "Arabic")
        self.assertNotIn("units", student.load_student())
        student.save_student("Example", "10", "Israel", "Arabic", "4")
        self.assertEqual(student.load_student()["units"], "4")

    def test_new_onboarding_asks_units(self):
        with patch("builtins.input", side_effect=["Example", "10", "Israel", "Arabic", "4", "Question"]), contextlib.redirect_stdout(io.StringIO()):
            main.main()
        self.assertEqual(student.load_student()["units"], "4")
        self.assertIn("Synthetic 4 units fixture", ai.client.responses.parse.call_args.kwargs["instructions"])

    @unittest.expectedFailure
    def test_known_gap_corrupt_json_graceful_read(self):
        progress.PROGRESS_FILE.write_text("{truncated", encoding="utf-8")
        before = progress.PROGRESS_FILE.read_bytes()
        progress.load_progress()  # Current code raises JSONDecodeError.
        self.assertEqual(progress.PROGRESS_FILE.read_bytes(), before)

    @unittest.expectedFailure
    def test_known_gap_wrong_json_shape_rejected(self):
        progress.PROGRESS_FILE.write_text("[]", encoding="utf-8")
        self.assertIsInstance(progress.load_progress(), dict)

    @unittest.expectedFailure
    def test_known_gap_timeout_graceful_reply(self):
        before = self.seed()
        ai.client.responses.parse.side_effect = TimeoutError("Synthetic timeout")
        reply = ai.ask_ai("Example", "7", "Testland", "English", "Question")
        self.assertIsInstance(reply, str)
        self.assert_preserved(before)

    @unittest.expectedFailure
    def test_known_gap_atomic_progress_and_history(self):
        before = self.seed()
        with patch.object(ai, "save_history", side_effect=OSError("Synthetic disk failure")):
            try:
                self.ask(result(True, True))
            except OSError:
                pass
        self.assert_preserved(before)

    @unittest.skip("Multi-student storage remains out of scope; single-tester Flask access is tested in tests/local")
    def test_future_flask_student_isolation(self):
        pass

    @unittest.skip("CLI JSON has no request IDs; local Flask deduplication is tested separately in tests/local")
    def test_future_retry_deduplication(self):
        pass


if __name__ == "__main__":
    unittest.main()
