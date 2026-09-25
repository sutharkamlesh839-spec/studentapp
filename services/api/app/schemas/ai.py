from pydantic import Field

from app.schemas.common import APIModel


class AIAssistRequest(APIModel):
    prompt: str = Field(min_length=3, max_length=4000)
    context: str | None = Field(default=None, max_length=4000)


class AIAssistResponse(APIModel):
    answer: str
    model: str
    disclaimer: str
