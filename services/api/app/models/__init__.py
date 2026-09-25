# Import every model here so Alembic sees one complete metadata registry.
from app.models.audit import AuditLog
from app.models.learning import (
    MCQQuestion,
    MCQResponse,
    Notification,
    PracticeTest,
    RevisionItem,
    StudyPlanTask,
    SupportQuery,
    SyllabusItem,
    TestAttempt,
)
from app.models.ops import OfficialUpdate, Opportunity, PaperSubmission, VideoLesson
from app.models.profiles import FacultyProfile, StudentProfile
from app.models.rbac import Permission, Role, role_permissions, user_roles
from app.models.resources import Resource, ResourceBookmark, ResourceProgress
from app.models.sessions import RefreshToken, UserSession
from app.models.user import User

__all__ = [
    "AuditLog",
    "FacultyProfile",
    "MCQQuestion",
    "MCQResponse",
    "Notification",
    "OfficialUpdate",
    "Opportunity",
    "PaperSubmission",
    "PracticeTest",
    "RevisionItem",
    "StudyPlanTask",
    "SyllabusItem",
    "SupportQuery",
    "TestAttempt",
    "Permission",
    "RefreshToken",
    "Resource",
    "ResourceBookmark",
    "ResourceProgress",
    "Role",
    "StudentProfile",
    "User",
    "UserSession",
    "VideoLesson",
    "role_permissions",
    "user_roles",
]
