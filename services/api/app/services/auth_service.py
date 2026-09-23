from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, generate_refresh_token, hash_refresh_token, verify_password
from app.models.profiles import StudentProfile
from app.models.rbac import Role
from app.models.sessions import RefreshToken, UserSession
from app.models.user import User


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class AuthService:
    @staticmethod
    async def roles_for_user(db: AsyncSession, user: User) -> list[str]:
        if user.roles:
            return [role.code for role in user.roles]
        result = await db.execute(select(Role).join(User.roles).where(User.id == user.id))
        return [role.code for role in result.scalars().all()]

    @staticmethod
    async def user_response(db: AsyncSession, user: User):
        roles = await AuthService.roles_for_user(db, user)
        student = await db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
        from app.schemas.auth import UserResponse

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            status=user.status,
            roles=roles,
            student_level=student.level if student else None,
            student_group=student.group_name if student else None,
        )

    @staticmethod
    async def create_session(db: AsyncSession, user: User, *, user_agent: str | None = None, ip_hash: str | None = None) -> tuple[str, UserSession]:
        now = datetime.now(UTC)
        session = UserSession(
            user_id=user.id,
            user_agent=user_agent,
            ip_hash=ip_hash,
            expires_at=now + timedelta(days=settings.refresh_token_days),
        )
        db.add(session)
        await db.flush()
        refresh_token = generate_refresh_token()
        db.add(RefreshToken(
            session_id=session.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=now + timedelta(days=settings.refresh_token_days),
        ))
        return refresh_token, session

    @staticmethod
    def set_auth_cookies(response, access_token: str, refresh_token: str | None = None) -> None:
        response.set_cookie("access_token", access_token, httponly=True, secure=settings.app_env == "production", samesite="lax", max_age=settings.access_token_minutes * 60, path="/")
        if refresh_token:
            response.set_cookie("refresh_token", refresh_token, httponly=True, secure=settings.app_env == "production", samesite="lax", max_age=settings.refresh_token_days * 86400, path="/api/v1/auth")

    @staticmethod
    def clear_auth_cookies(response) -> None:
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/api/v1/auth")

    @staticmethod
    async def refresh(db: AsyncSession, raw_token: str) -> tuple[str, str, User]:
        now = datetime.now(UTC)
        stored = await db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw_token)))
        if not stored:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session is invalid or expired")
        if stored.rotated_at:
            await AuthService.revoke_refresh_family(db, stored.session_id)
            await db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token reuse detected")
        if stored.revoked_at or as_utc(stored.expires_at) <= now:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session is invalid or expired")
        session = await db.get(UserSession, stored.session_id)
        if not session or session.revoked_at or as_utc(session.expires_at) <= now:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired")
        user = await db.get(User, session.user_id)
        if not user or not user.is_active or user.deleted_at:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is unavailable")

        stored.rotated_at = now
        new_refresh, _ = await AuthService.create_session_token(db, session, now)
        access = create_access_token(user_id=str(user.id), session_id=str(session.id), role_codes=await AuthService.roles_for_user(db, user))
        return access, new_refresh, user

    @staticmethod
    async def create_session_token(db: AsyncSession, session: UserSession, now: datetime) -> tuple[str, RefreshToken]:
        raw = generate_refresh_token()
        stored = RefreshToken(
            session_id=session.id,
            token_hash=hash_refresh_token(raw),
            expires_at=min(as_utc(session.expires_at), now + timedelta(days=settings.refresh_token_days)),
        )
        db.add(stored)
        return raw, stored

    @staticmethod
    async def revoke_refresh_family(db: AsyncSession, session_id: UUID) -> None:
        now = datetime.now(UTC)
        session = await db.get(UserSession, session_id)
        if session:
            session.revoked_at = now
        result = await db.execute(select(RefreshToken).where(RefreshToken.session_id == session_id, RefreshToken.revoked_at.is_(None)))
        for token in result.scalars().all():
            token.revoked_at = now

    @staticmethod
    def validate_password(password: str) -> None:
        if len(password) < 8 or password.lower() == password or password.upper() == password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be 8+ characters with upper and lower case letters")

    @staticmethod
    def authenticate(user: User | None, password: str) -> User:
        if not user or not user.is_active or user.deleted_at or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")
        return user

    @staticmethod
    def decode(token: str) -> dict:
        try:
            return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"], issuer=settings.jwt_issuer)
        except jwt.PyJWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is invalid or expired") from exc
