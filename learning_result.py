import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, model_validator

QUESTION_MARKS = "?؟？"
MODES = ("explain", "practice", "plan", "bagrut")
_QUESTION_MARK = re.compile("[" + QUESTION_MARKS + "]")
# End of a sentence: a question/exclamation mark, a line break, or a full stop that is not a decimal point.
_SENTENCE_END = re.compile("[!" + QUESTION_MARKS + r"\n]|\.(?=\s|$)")


def strip_question_marks(text):
    """A short practice explanation asks nothing: every question mark becomes a full stop."""
    return re.sub("\\s*[" + QUESTION_MARKS + "]+", ".", text)


def _last_question_bounds(text):
    """(start, end) of the sentence that holds the last question mark, or None."""
    marks = [match.start() for match in _QUESTION_MARK.finditer(text)]
    if not marks:
        return None
    end = marks[-1]
    start = max((match.end() for match in _SENTENCE_END.finditer(text[:end])), default=0)
    return start, end + 1


def last_question(text):
    """One question: with more than one question mark keep only the last question sentence."""
    bounds = _last_question_bounds(text)
    if bounds is None or len(_QUESTION_MARK.findall(text)) <= 1:
        return text.strip()
    return text[bounds[0]:bounds[1]].strip()


def has_reply_text(raw):
    """True for a model answer with explanation and question, or for the older single `reply` field."""
    return isinstance(raw, dict) and (isinstance(raw.get("reply"), str)
                                      or (isinstance(raw.get("explanation"), str) and isinstance(raw.get("question"), str)))


class LearningResult(BaseModel):
    model_config = ConfigDict(revalidate_instances="always")

    mode: Literal["explain", "practice", "plan", "bagrut"] = Field(description=(
        "The mode of this reply, chosen from the student's latest message (the intent label is only a hint). "
        "'explain': the student does not understand, asks for an explanation, asks what something means or why, "
        "or asks to start or learn a topic. 'practice': the student sends a solution, an answer or an exercise. "
        "'plan': the student asks for a study plan for the Bagrut or an exam. 'bagrut': the student asks to "
        "practise a Bagrut-style question, or sends the solution of a section of one."))
    explanation: str = Field(description=(
        "The teaching part of the reply, in the student's own dialect, written in Markdown. In every mode it never "
        "writes the words 'الملف', 'ملف المنهاج' or 'ملفات' (or 'the file'): say 'منهاجك' or name the topic. It contains NO question "
        "marks at all (neither ? nor ؟) and asks nothing: the only question goes in `question`. It must never "
        "state the final answer of the student's own exercise. What it contains depends on the mode. "
        "PRACTICE: short, with bullet points. Name the exact mistake and why it happened. It must never calculate, "
        "factor, substitute or otherwise do the step that the question asks the student to do. When the student's "
        "step is wrong, say which step is wrong and what kind of mistake it is, but never write the corrected "
        "version of that step (the right expression, value, formula or list of right terms), not even partly: "
        "the student writes the correction in answer to the question. Keep it short: at most five sentences and "
        "ONE idea. No second idea, no side remark such as 'we can also...', no extra analogy on top of the main "
        "one, and no derivation or proof unless the student asked for one. "
        "EXPLAIN: a short, direct explanation of about 150 words in light Markdown only (**bold** and bullet "
        "points, no headings, no introduction, no story). The first sentence says what the topic is, in simple "
        "words. Then the rule or formula on a line of its own between $$ and $$, and one bullet for each symbol "
        "with its meaning. Then ONE solved example, step by step with numbered steps, using numbers different "
        "from the student's own exercise. Never write topic ids or the word 'file', and never mention the Bagrut "
        "or the exam unless the student asked about it. If the student still does not understand, explain it in "
        "a different way, not with the same words. "
        "PLAN: a study plan split into weeks, as a table or a numbered list: the week, the topic with its id from "
        "the curriculum file, and what to do; with the exam form number given in the file. Only topics of the file. "
        "BAGRUT: when the student asks for a question, the short real-life story with all its numbers and nothing "
        "else (the section itself goes in `question`); when the student sent a solution, the feedback: a right "
        "solution is confirmed in one or two lines, a wrong one gets the exact mistake and one small hint. Never "
        "show the sections that are not being asked yet and never give an answer."))
    question: str = Field(description=(
        "Exactly one short question for the student, in every mode, with a single question mark. It asks for ONE "
        "small next step (for example one substitution, one factorisation or one value), not a whole solution; in "
        "explain and plan mode it is one light question. It must not contain the answer to that step and must not "
        "open a second topic. It asks for one value or one step only: never join two requests with 'and', 'then', "
        "'after that' or 'how' (in Arabic: و, وبعدها, وكيف, ثم). If two steps are needed, ask only about the first one. "
        "In bagrut mode only, it is the text of the one section being asked, labelled 'القسم أ', 'القسم ب' and so on, "
        "written as a task such as 'جد ...' or 'علّل ...' with items (1) and (2) on separate lines and at most one "
        "question mark."))

    answer_key: str | None = Field(default=None, description=(
        "HIDDEN: it is saved but never shown to the student. In bagrut mode only, and only when you write a NEW "
        "question (the reply that gives section 'القسم أ' for the first time): the complete correct solution of EVERY "
        "section, with the steps and the final values. Compute it carefully BEFORE you write the question. If any "
        "number does not come out clean, change the numbers of the question and compute again before you send it. "
        "Null in every other reply (the saved key stays), and never copy any part of it into the explanation or the "
        "question."))

    is_attempt: bool

    subject: StrictStr | None = None
    topic: StrictStr | None = None
    skill: StrictStr | None = None

    correct: StrictBool | None = None
    hint_used: StrictBool | None = None
    mistake_type: str | None = None

    @model_validator(mode="before")
    @classmethod
    def accept_older_shapes(cls, data):
        if not isinstance(data, dict):
            return data
        data = dict(data)
        # Results saved or produced before modes existed are practice replies.
        data.setdefault("mode", "practice")
        # Older callers and tests supply one `reply` string: its last question becomes `question`.
        if "reply" in data and "explanation" not in data and "question" not in data:
            reply = data.pop("reply")
            if isinstance(reply, str):
                bounds = _last_question_bounds(reply)
                if bounds is None:
                    data["explanation"], data["question"] = reply, ""
                else:
                    data["explanation"] = (reply[:bounds[0]] + reply[bounds[1]:]).strip()
                    data["question"] = reply[bounds[0]:bounds[1]].strip()
        return data

    @model_validator(mode="after")
    def normalise_text(self):
        # Practice replies are short, so a stray question mark is turned into a full stop. Explain and plan replies
        # are Markdown (headings, tables): their text is left as the model wrote it. The question is always one.
        if self.mode == "practice":
            self.explanation = strip_question_marks(self.explanation)
        self.question = last_question(self.question)
        # The answer key exists only in bagrut mode, and it is never part of what the student reads.
        key = (self.answer_key or "").strip()
        self.answer_key = key if key and self.mode == "bagrut" else None
        if self.answer_key and (self.answer_key in self.explanation or self.answer_key in self.question):
            raise ValueError("the answer key must never be copied into the reply")
        return self

    @property
    def reply(self):
        """What the student sees and what is saved to the history: explanation, then question."""
        return "\n\n".join(part.strip() for part in (self.explanation, self.question) if part.strip())

    @model_validator(mode="after")
    def validate_attempt(self):
        if self.is_attempt:
            for field in ("subject", "topic", "skill"):
                value = getattr(self, field)
                if value is None or not value.strip():
                    raise ValueError(f"{field} must be non-empty for a learning attempt")

            if self.correct is None or self.hint_used is None:
                raise ValueError("correct and hint_used must be booleans for a learning attempt")

        return self
