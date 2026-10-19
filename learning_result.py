import re

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, field_validator, model_validator

QUESTION_MARKS = "?؟？"
_QUESTION_MARK = re.compile("[" + QUESTION_MARKS + "]")
# End of a sentence: a question/exclamation mark, a line break, or a full stop that is not a decimal point.
_SENTENCE_END = re.compile("[!" + QUESTION_MARKS + r"\n]|\.(?=\s|$)")


def strip_question_marks(text):
    """An explanation asks nothing: every question mark becomes a full stop."""
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

    explanation: str = Field(description=(
        "The teaching part of the reply, in the student's language. It contains NO question marks at all "
        "(neither ? nor ؟) and asks nothing. Name the exact mistake if there is one, explain why it happened, "
        "and give at most one small hint. It must never calculate, factor, substitute or otherwise do the step "
        "that the question asks the student to do, and it must never state the final answer."))
    question: str = Field(description=(
        "Exactly one short question for the student, with a single question mark. It asks for ONE small next "
        "step (for example one substitution, one factorisation or one value), not a whole solution. It must not "
        "contain the answer to that step and must not open a second topic."))

    is_attempt: bool

    subject: StrictStr | None = None
    topic: StrictStr | None = None
    skill: StrictStr | None = None

    correct: StrictBool | None = None
    hint_used: StrictBool | None = None
    mistake_type: str | None = None

    @model_validator(mode="before")
    @classmethod
    def accept_single_reply(cls, data):
        # Older callers and tests supply one `reply` string: its last question becomes `question`.
        if isinstance(data, dict) and "reply" in data and "explanation" not in data and "question" not in data:
            data = dict(data)
            reply = data.pop("reply")
            if isinstance(reply, str):
                bounds = _last_question_bounds(reply)
                if bounds is None:
                    data["explanation"], data["question"] = reply, ""
                else:
                    data["explanation"] = (reply[:bounds[0]] + reply[bounds[1]:]).strip()
                    data["question"] = reply[bounds[0]:bounds[1]].strip()
        return data

    @field_validator("explanation")
    @classmethod
    def explanation_has_no_question(cls, value):
        return strip_question_marks(value)

    @field_validator("question")
    @classmethod
    def question_is_one_question(cls, value):
        return last_question(value)

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
