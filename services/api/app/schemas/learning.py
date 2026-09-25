from datetime import date, datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import APIModel


class MCQCreate(APIModel):
    prompt: str = Field(min_length=5, max_length=5000)
    options: list[str] = Field(min_length=2, max_length=6)
    correct_option: int = Field(ge=0)
    explanation: str = Field(min_length=2, max_length=5000)
    subject: str = Field(min_length=2, max_length=120)
    chapter: str | None = Field(default=None, max_length=160)
    difficulty: str = Field(default="medium", max_length=30)

    @field_validator("correct_option")
    @classmethod
    def valid_answer_index(cls, value: int, info):
        options = info.data.get("options", [])
        if options and value >= len(options):
            raise ValueError("correct_option must point to an option")
        return value


class MCQResponse(APIModel):
    id: UUID
    prompt: str
    options: list[str]
    explanation: str | None = None
    subject: str
    chapter: str | None
    difficulty: str
    created_at: datetime


class MCQAnswerRequest(APIModel):
    selected_option: int = Field(ge=0)


class MCQAnswerResponse(APIModel):
    correct: bool
    correct_option: int
    explanation: str
    score: int


class MCQMistakeResponse(APIModel):
    id: UUID
    question_id: UUID
    prompt: str
    subject: str
    chapter: str | None
    selected_option: int
    correct_option: int
    explanation: str
    created_at: datetime


class SyllabusCreate(APIModel):
    subject: str = Field(min_length=2, max_length=120)
    chapter: str = Field(min_length=2, max_length=160)
    total_topics: int = Field(default=1, ge=1, le=1000)
    completed_topics: int = Field(default=0, ge=0)


class SyllabusUpdate(APIModel):
    completed_topics: int = Field(ge=0)
    status: str = Field(default="in_progress", max_length=30)


class SyllabusResponse(APIModel):
    id: UUID
    subject: str
    chapter: str
    total_topics: int
    completed_topics: int
    status: str
    progress: float
    updated_at: datetime


class PlanTaskCreate(APIModel):
    title: str = Field(min_length=2, max_length=220)
    subject: str | None = Field(default=None, max_length=120)
    due_date: date
    minutes: int = Field(default=30, ge=5, le=1440)


class PlanTaskUpdate(APIModel):
    completed: bool


class PlanTaskResponse(APIModel):
    id: UUID
    title: str
    subject: str | None
    due_date: date
    minutes: int
    completed: bool
    created_at: datetime


class RevisionCreate(APIModel):
    title: str = Field(min_length=2, max_length=220)
    subject: str | None = Field(default=None, max_length=120)
    due_at: datetime


class RevisionUpdate(APIModel):
    status: str = Field(max_length=30)


class RevisionResponse(APIModel):
    id: UUID
    title: str
    subject: str | None
    due_at: datetime
    status: str
    created_at: datetime


class TestCreate(APIModel):
    title: str = Field(min_length=2, max_length=220)
    description: str | None = Field(default=None, max_length=5000)
    duration_minutes: int = Field(default=60, ge=1, le=600)
    marks: int = Field(default=0, ge=0, le=10000)
    question_ids: list[UUID] = Field(default_factory=list)
    status: str = Field(default="open", max_length=30)


class TestResponse(APIModel):
    id: UUID
    title: str
    description: str | None
    duration_minutes: int
    marks: int
    question_count: int
    status: str
    created_at: datetime


class TestSubmitRequest(APIModel):
    answers: dict[str, int]


class TestAttemptResponse(APIModel):
    id: UUID
    test_id: UUID
    score: float
    total_questions: int
    correct_answers: int
    submitted_at: datetime


class QueryCreate(APIModel):
    subject: str = Field(min_length=2, max_length=120)
    title: str = Field(min_length=2, max_length=220)
    body: str = Field(min_length=5, max_length=10000)


class QueryReply(APIModel):
    answer: str = Field(min_length=2, max_length=10000)


class QueryResponse(APIModel):
    id: UUID
    subject: str
    title: str
    body: str
    answer: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class NotificationResponse(APIModel):
    id: UUID
    title: str
    body: str
    kind: str
    read_at: datetime | None
    created_at: datetime


class AnalyticsSummary(APIModel):
    mcq_attempts: int
    mcq_accuracy: float
    completed_resources: int
    completed_tasks: int
    pending_revision: int
    test_attempts: int
    open_queries: int
