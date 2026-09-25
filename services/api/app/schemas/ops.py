from datetime import datetime
from uuid import UUID

from pydantic import Field, HttpUrl

from app.schemas.common import APIModel


class VideoCreate(APIModel):
    title: str = Field(min_length=2, max_length=220)
    description: str | None = Field(default=None, max_length=5000)
    level: str = Field(min_length=2, max_length=40)
    subject: str = Field(min_length=2, max_length=120)
    chapter: str | None = Field(default=None, max_length=160)
    video_url: HttpUrl
    duration_minutes: int = Field(default=30, ge=1, le=600)


class VideoResponse(APIModel):
    id: UUID
    title: str
    description: str | None
    level: str
    subject: str
    chapter: str | None
    video_url: str
    duration_minutes: int
    created_at: datetime


class OpportunityCreate(APIModel):
    kind: str = Field(pattern="^(career|articleship)$")
    title: str = Field(min_length=2, max_length=220)
    organisation: str | None = Field(default=None, max_length=180)
    location: str | None = Field(default=None, max_length=160)
    description: str = Field(min_length=5, max_length=10000)
    application_url: HttpUrl | None = None
    target_level: str | None = Field(default=None, max_length=40)


class OpportunityResponse(APIModel):
    id: UUID
    kind: str
    title: str
    organisation: str | None
    location: str | None
    description: str
    application_url: str | None
    target_level: str | None
    created_at: datetime


class OfficialUpdateCreate(APIModel):
    title: str = Field(min_length=2, max_length=220)
    body: str = Field(min_length=5, max_length=10000)
    category: str = Field(min_length=2, max_length=80)
    source_url: HttpUrl


class OfficialUpdateResponse(APIModel):
    id: UUID
    title: str
    body: str
    category: str
    source_url: str
    published_at: datetime


class PaperEvaluate(APIModel):
    marks: float = Field(ge=0, le=1000)
    feedback: str = Field(min_length=2, max_length=10000)


class PaperAssign(APIModel):
    faculty_id: UUID


class PaperResponse(APIModel):
    id: UUID
    title: str
    subject: str
    file_name: str | None
    annotated_file_name: str | None
    status: str
    marks: float | None
    feedback: str | None
    assigned_to: UUID | None
    created_at: datetime
    evaluated_at: datetime | None


class AdminUserResponse(APIModel):
    id: UUID
    email: str
    full_name: str
    status: str
    roles: list[str]
    created_at: datetime


class AuditLogResponse(APIModel):
    id: UUID
    actor_id: UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    after_state: dict | None
    created_at: datetime
