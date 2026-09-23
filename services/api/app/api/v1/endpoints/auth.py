from datetime import UTC, datetime

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from sqlalchemy import select

from app.api.deps import DB, CurrentUser
from app.core.security import create_access_token, hash_password, hash_refresh_token
from app.models.profiles import StudentProfile
from app.models.rbac import Role
from app.models.sessions import RefreshToken
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RefreshRequest, RegisterRequest, UserResponse
from app.schemas.common import MessageResponse
from app.services.audit_service import record_audit
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def normalized_email(email: str) -> str:
    return email.strip().lower()


async def auth_response(db: DB, user: User, access_token: str) -> AuthResponse:
    return AuthResponse(
        access_token=access_token,
        expires_in=15 * 60,
        user=await AuthService.user_response(db, user),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, request: Request, response: Response, db: DB) -> AuthResponse:
    email = normalized_email(str(payload.email))
    if await db.scalar(select(User).where(User.normalized_email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    AuthService.validate_password(payload.password)
    student_role = await db.scalar(select(Role).where(Role.code == "student"))
    if not student_role:
        student_role = Role(code="student", name="Student", is_system=True)
        db.add(student_role)
        await db.flush()

    user = User(
        email=email,
        normalized_email=email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        mobile=payload.mobile,
    )
    user.roles.append(student_role)
    db.add(user)
    await db.flush()
    db.add(
        StudentProfile(
            user_id=user.id,
            level=payload.level,
            group_name=payload.group_name,
            current_attempt=payload.current_attempt,
        )
    )
    refresh_token, session = await AuthService.create_session(db, user, user_agent=request.headers.get("user-agent"))
    access_token = create_access_token(
        user_id=str(user.id),
        session_id=str(session.id),
        role_codes=["student"],
    )
    await record_audit(
        db,
        actor_id=user.id,
        action="auth.registered",
        resource_type="user",
        resource_id=str(user.id),
        request_id=request.headers.get("x-request-id"),
    )
    await db.commit()
    AuthService.set_auth_cookies(response, access_token, refresh_token)
    return await auth_response(db, user, access_token)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, request: Request, response: Response, db: DB) -> AuthResponse:
    email = normalized_email(str(payload.email))
    user = await db.scalar(select(User).where(User.normalized_email == email))
    user = AuthService.authenticate(user, payload.password)
    user.last_login_at = datetime.now(UTC)
    refresh_token, session = await AuthService.create_session(db, user, user_agent=request.headers.get("user-agent"))
    access_token = create_access_token(
        user_id=str(user.id),
        session_id=str(session.id),
        role_codes=await AuthService.roles_for_user(db, user),
    )
    await record_audit(
        db,
        actor_id=user.id,
        action="auth.logged_in",
        resource_type="session",
        resource_id=str(session.id),
        request_id=request.headers.get("x-request-id"),
    )
    await db.commit()
    AuthService.set_auth_cookies(response, access_token, refresh_token)
    return await auth_response(db, user, access_token)


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    response: Response,
    db: DB,
    payload: RefreshRequest | None = None,
    refresh_cookie: str | None = Cookie(default=None, alias="refresh_token"),
) -> AuthResponse:
    raw_token = refresh_cookie or (payload.refresh_token if payload else None)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required")
    access_token, new_refresh, user = await AuthService.refresh(db, raw_token)
    await db.commit()
    AuthService.set_auth_cookies(response, access_token, new_refresh)
    return await auth_response(db, user, access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    db: DB,
    _current_user: CurrentUser,
    refresh_cookie: str | None = Cookie(default=None, alias="refresh_token"),
) -> MessageResponse:
    if refresh_cookie:
        stored = await db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(refresh_cookie))
        )
        if stored:
            await AuthService.revoke_refresh_family(db, stored.session_id)
    await db.commit()
    AuthService.clear_auth_cookies(response)
    return MessageResponse(message="Signed out securely")


@router.get("/me", response_model=UserResponse)
async def me(db: DB, current_user: CurrentUser) -> UserResponse:
    return await AuthService.user_response(db, current_user)
