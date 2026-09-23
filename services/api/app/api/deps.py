from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.rbac import Permission, role_permissions, user_roles
from app.models.sessions import UserSession
from app.models.user import User

bearer = HTTPBearer(auto_error=False)
DB = Annotated[AsyncSession, Depends(get_db)]


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


async def get_current_user(
    request: Request,
    db: DB,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = decode_access_token(token)
        user_id = UUID(payload["sub"])
        session_id = UUID(payload["sid"])
    except (KeyError, TypeError, ValueError, jwt.PyJWTError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is invalid") from None

    session = await db.get(UserSession, session_id)
    if not session or session.revoked_at or as_utc(session.expires_at) <= datetime.now(UTC) or session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired")
    user = await db.get(User, user_id)
    if not user or not user.is_active or user.deleted_at:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is unavailable")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*required_roles: str) -> Callable[..., Awaitable[User]]:
    async def dependency(user: CurrentUser) -> User:
        current_roles = {role.code for role in user.roles}
        if not current_roles.intersection(required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this area")
        return user

    return dependency


def require_permission(permission_code: str) -> Callable[..., Awaitable[User]]:
    async def dependency(user: CurrentUser, db: DB) -> User:
        assigned_roles = select(user_roles.c.role_id).where(user_roles.c.user_id == user.id)
        permission = await db.scalar(
            select(Permission.id)
            .join(role_permissions, role_permissions.c.permission_id == Permission.id)
            .where(
                Permission.code == permission_code,
                role_permissions.c.role_id.in_(assigned_roles),
            )
        )
        if permission is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing required permission")
        return user

    return dependency
