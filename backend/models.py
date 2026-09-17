from pydantic import Field, BaseModel, field_validator


class AskRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="User question"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:

        trimmed = value.strip()

        if not trimmed:
            raise ValueError(
                "Question cannot be empty or whitespace only."
            )

        word_count = len(trimmed.split())

        if word_count > 300:
            raise ValueError(
                f"Question exceeds the 300-word limit "
                f"(currently {word_count} words)."
            )

        return trimmed


class SourceCitation(BaseModel):
    document: str
    line:int
   

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceCitation]
    mode: str