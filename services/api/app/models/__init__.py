# Import every model here so Alembic sees one complete metadata registry.
from app.models.audit import AuditLog
from app.models.profiles import FacultyProfile, StudentProfile
from app.models.rbac import Permission, Role, role_permissions, user_roles
from app.models.sessions import RefreshToken, UserSession
from app.models.user import User

__all__ = [
    "AuditLog",
    "FacultyProfile",
    "Permission",
    "RefreshToken",
    "Role",
    "StudentProfile",
    "User",
    "UserSession",
    "role_permissions",
    "user_roles",
]
