"""Offline contracts only; fake OpenAI is installed before importing ai_test."""
import contextlib
import importlib
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
fake_openai = ModuleType("openai")
fake_openai.OpenAI = Mock(return_value=SimpleNamespace(responses=SimpleNamespace(parse=Mock())))
sys.modules["openai"] = fake_openai
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
                                        (student, "STUDENT_FILE", "student.json"),
                                        (curriculum, "CURRICULUM_FILE", "curriculum.txt")]:
            self.stack.enter_context(patch.object(module, name, self.base / filename))
        curriculum.CURRICULUM_FILE.write_text("Synthetic curriculum: no country markers.", encoding="utf-8")
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
        with patch("builtins.input", side_effect=["Example", "7", "Testland", "Arabic", "Question"]), contextlib.redirect_stdout(io.StringIO()):
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

    def test_matching_curriculum(self):
        curriculum.CURRICULUM_FILE.write_text("[CURRICULUM:TESTLAND:7]Synthetic fixture only[/CURRICULUM]", encoding="utf-8")
        self.assertEqual(curriculum.get_curriculum("testland", "7"), "Synthetic fixture only")

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
