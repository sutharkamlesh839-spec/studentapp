from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, EmailStr, Field, field_validator

from app.schemas.common import APIModel


class RegisterRequest(APIModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    mobile: str | None = Field(default=None, min_length=7, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    level: str = Field(default="CA Intermediate", min_length=2, max_length=40)
    group_name: str | None = Field(default=None, max_length=40)
    current_attempt: str | None = Field(default=None, max_length=50)

    @field_validator("full_name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Full name is required")
        return value


class LoginRequest(APIModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(APIModel):
    refresh_token: str | None = None


class UserResponse(APIModel):
    id: UUID
    email: EmailStr
    full_name: str
    status: str
    roles: list[str]
    student_level: str | None = None
    student_group: str | None = None
    student_attempt: str | None = None


class AuthResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class DashboardSummary(APIModel):
    user: UserResponse
    preparation_score: int | None = None
    syllabus_completion: float | None = None
    next_actions: list[str] = []
    data_status: str = "awaiting_activity"


class SessionResponse(APIModel):
    id: UUID
    device_name: str | None
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
