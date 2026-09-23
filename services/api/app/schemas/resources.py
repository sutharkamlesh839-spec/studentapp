from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import APIModel


class ResourceResponse(APIModel):
    id: UUID
    title: str
    description: str | None
    level: str
    group_name: str | None
    subject: str
    chapter: str | None
    resource_type: str
    attempt: str | None
    year: int | None
    source: str | None
    file_name: str | None
    file_size: int | None
    mime_type: str | None
    official_icai: bool
    is_active: bool
    bookmarked: bool = False
    completed: bool = False
    created_at: datetime


class ResourceCreate(APIModel):
    title: str = Field(min_length=2, max_length=220)
    description: str | None = Field(default=None, max_length=4000)
    level: str = Field(min_length=2, max_length=40)
    group_name: str | None = Field(default=None, max_length=40)
    subject: str = Field(min_length=2, max_length=120)
    chapter: str | None = Field(default=None, max_length=160)
    resource_type: str = Field(min_length=2, max_length=60)
    attempt: str | None = Field(default=None, max_length=60)
    year: int | None = Field(default=None, ge=2000, le=2100)
    source: str | None = Field(default=None, max_length=500)
    official_icai: bool = False


class ResourceProgressRequest(APIModel):
    completed: bool
