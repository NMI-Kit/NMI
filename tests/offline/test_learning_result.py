"""explanation + question: the reply is built in code, so a second question cannot reach the student."""
import importlib
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
from learning_result import LearningResult, has_reply_text, last_question, strip_question_marks


def make(**values):
    return LearningResult(**({"explanation": "شرح.", "question": "شو الخطوة؟", "is_attempt": False} | values))


class SchemaTests(unittest.TestCase):
    def test_model_sees_explanation_and_question_but_not_reply(self):
        schema = LearningResult.model_json_schema()
        self.assertTrue({"explanation", "question", "is_attempt"} <= set(schema["required"]))
        self.assertNotIn("reply", schema["properties"])
        self.assertLess(list(schema["properties"]).index("explanation"), list(schema["properties"]).index("question"))

    def test_descriptions_say_what_each_field_may_contain(self):
        properties = LearningResult.model_json_schema()["properties"]
        explanation, question = properties["explanation"]["description"], properties["question"]["description"]
        self.assertIn("NO question marks", explanation)
        self.assertIn("never calculate, factor, substitute", explanation.lower().replace("it must ", ""))
        self.assertIn("never state the final answer", explanation)
        self.assertIn("Exactly one short question", question)
        self.assertIn("ONE small next step", question)
        self.assertIn("must not contain the answer", question)


class ExplanationTests(unittest.TestCase):
    def test_question_marks_become_full_stops(self):
        self.assertEqual(make(explanation="شو الحل؟ وليش? ثم؟؟").explanation, "شو الحل. وليش. ثم.")
        self.assertEqual(strip_question_marks("a？ b"), "a. b")
        self.assertEqual(make(explanation="بدون سؤال.").explanation, "بدون سؤال.")

    def test_conversion_is_idempotent(self):
        once = make(explanation="هل فهمت؟")
        self.assertEqual(LearningResult.model_validate(once).explanation, once.explanation)
        self.assertEqual(LearningResult.model_validate(once.model_dump()).reply, once.reply)


class QuestionTests(unittest.TestCase):
    def test_one_question_is_kept_as_it_is(self):
        self.assertEqual(make(question="  شو قيمة cos 60°؟ ").question, "شو قيمة cos 60°؟")
        self.assertEqual(make(question="جرّب خطوة وحدة").question, "جرّب خطوة وحدة")

    def test_more_than_one_question_mark_keeps_the_last_question_sentence(self):
        self.assertEqual(make(question="شو cos 60°؟ وبعدها حاول تحسب؟").question, "وبعدها حاول تحسب؟")
        self.assertEqual(make(question="أولاً شرح. شو العامل؟ وأي واحد بينختصر؟").question, "وأي واحد بينختصر؟")
        self.assertEqual(make(question="What is x? What is y?").question, "What is y?")
        self.assertEqual(make(question="a?\nb?\nكم 3.5 × 2؟").question, "كم 3.5 × 2؟")  # a decimal point is not a sentence end
        self.assertEqual(make(question="شو الحل؟ جرّب بعدها.").question, "شو الحل؟ جرّب بعدها.")  # one mark: unchanged
        self.assertEqual(last_question("a؟ b؟ c؟ trailing"), "c؟")

    def test_reply_is_explanation_then_question(self):
        result = make(explanation="  الخطأ بالإشارة.  ", question=" شو بيصير؟ ")
        self.assertEqual(result.reply, "الخطأ بالإشارة.\n\nشو بيصير؟")
        self.assertEqual(make(question="").reply, "شرح.")
        self.assertEqual(make(explanation="").reply, "شو الخطوة؟")


class LegacyReplyTests(unittest.TestCase):
    def test_old_single_reply_is_split_at_its_last_question(self):
        result = LearningResult(reply="الخطأ في إشارة القسمة. ماذا يحدث عند قسمة 6 على −2؟", is_attempt=False)
        self.assertEqual((result.explanation, result.question), ("الخطأ في إشارة القسمة.", "ماذا يحدث عند قسمة 6 على −2؟"))
        self.assertEqual(result.reply, "الخطأ في إشارة القسمة.\n\nماذا يحدث عند قسمة 6 على −2؟")
        two = LearningResult(reply="شو cos 60°؟ وبعدها شو الناتج؟", is_attempt=False)
        self.assertEqual((two.explanation, two.question), ("شو cos 60°.", "وبعدها شو الناتج؟"))

    def test_old_reply_without_a_question_and_other_fields_still_work(self):
        result = LearningResult(reply="Synthetic tutor reply", is_attempt=False)
        self.assertEqual((result.explanation, result.question, result.reply), ("Synthetic tutor reply", "", "Synthetic tutor reply"))
        attempt = LearningResult(reply="جيد", is_attempt=True, subject="mathematics", topic="t", skill="s", correct=True, hint_used=False)
        self.assertTrue(attempt.correct)
        with self.assertRaises(ValueError):
            LearningResult(reply="x", is_attempt=True)  # attempt rules unchanged
        with self.assertRaises(ValueError):
            LearningResult(is_attempt=False)  # neither reply nor explanation/question

    def test_has_reply_text_accepts_both_shapes_only(self):
        self.assertTrue(has_reply_text({"reply": "x"}))
        self.assertTrue(has_reply_text({"explanation": "x", "question": ""}))
        for bad in ({}, {"explanation": "x"}, {"question": "x"}, {"reply": 1}, {"explanation": 1, "question": 2}, None, "x"):
            self.assertFalse(has_reply_text(bad), bad)


class AskAiTests(unittest.TestCase):
    def setUp(self):
        cache = ROOT / ".cache/offline"
        cache.mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=cache)
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        for module, name, filename in [(history, "HISTORY_FILE", "history.json"), (progress, "PROGRESS_FILE", "progress.json")]:
            patcher = patch.object(module, name, base / filename)
            patcher.start()
            self.addCleanup(patcher.stop)
        for target, attribute in ((socket.socket, "connect"), (socket, "create_connection")):
            patcher = patch.object(target, attribute, side_effect=AssertionError("Network forbidden"))
            patcher.start()
            self.addCleanup(patcher.stop)
        self.parse = Mock()
        patcher = patch.object(ai, "client", SimpleNamespace(responses=SimpleNamespace(parse=self.parse)))
        patcher.start()
        self.addCleanup(patcher.stop)

    def ask(self, parsed, **options):
        self.parse.return_value = SimpleNamespace(output_parsed=parsed, status="completed")
        return ai.ask_ai("Synthetic Student", "10", "Israel", "Arabic", "رسالة", **options)

    def test_the_student_and_the_history_get_explanation_then_one_question(self):
        reply = self.ask({"explanation": "الخطأ بالمشتقة؟ شوف.", "question": "شو مشتقة 5x؟ وشو f'(2)؟", "is_attempt": False})
        self.assertEqual(reply, "الخطأ بالمشتقة. شوف.\n\nوشو f'(2)؟")
        self.assertEqual(history.load_history()[-1], {"role": "assistant", "content": reply})
        self.assertEqual(reply.count("؟"), 1)

    def test_instance_results_are_normalised_the_same_way(self):
        reply = self.ask(LearningResult(explanation="شرح؟", question="أ؟ ب؟", is_attempt=False))
        self.assertEqual(reply, "شرح.\n\nب؟")

    def test_old_history_is_sent_unchanged_and_old_single_reply_still_works(self):
        old = [{"role": "user", "content": "سؤال قديم؟"}, {"role": "assistant", "content": "جواب قديم؟ بسؤالين؟"}]
        history.save_history(old)
        reply = self.ask({"reply": "تمام. شو الخطوة؟", "is_attempt": False})
        self.assertEqual(reply, "تمام.\n\nشو الخطوة؟")
        sent = self.parse.call_args.kwargs["input"]
        self.assertEqual(sent[:2], old)  # stored history is never rewritten
        self.assertEqual(history.load_history()[:2], old)

    def test_web_policy_requires_text_in_either_shape_and_records_attempts_as_before(self):
        for good in ({"explanation": "شرح.", "question": "سؤال؟", "is_attempt": False}, {"reply": "رد؟", "is_attempt": False}):
            self.assertTrue(self.ask(good, web_policy=True))
        for bad in ({"is_attempt": False}, {"explanation": "x", "is_attempt": False}, {"explanation": "", "question": " ", "is_attempt": False}):
            with self.subTest(bad=bad), self.assertRaises(ai.InvalidAIResponse):
                self.ask(bad, web_policy=True)
        history.save_history([{"role": "assistant", "content": "تمرين"}])
        self.ask({"explanation": "غلط.", "question": "جرّب؟", "is_attempt": True, "subject": "mathematics", "topic": "t",
                  "skill": "s", "correct": False, "hint_used": False}, web_policy=True, intent="answer")
        self.assertEqual(progress.load_progress()["attempts"][0]["correct"], False)


if __name__ == "__main__":
    unittest.main()
