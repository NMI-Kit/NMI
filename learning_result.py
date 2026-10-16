from pydantic import BaseModel, ConfigDict, StrictBool, StrictStr, model_validator


class LearningResult(BaseModel):
    model_config = ConfigDict(revalidate_instances="always")

    reply: str

    is_attempt: bool

    subject: StrictStr | None = None
    topic: StrictStr | None = None
    skill: StrictStr | None = None

    correct: StrictBool | None = None
    hint_used: StrictBool | None = None
    mistake_type: str | None = None

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