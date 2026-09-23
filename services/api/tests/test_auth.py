import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all Phase 0 tables with metadata
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app


@pytest.fixture
async def client():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_db():
        async with session_factory() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_db
    try:
        async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as test_client:
            yield test_client
    finally:
        fastapi_app.dependency_overrides.clear()
        await engine.dispose()


async def test_registration_login_and_refresh(client: AsyncClient) -> None:
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Priya Shah",
            "email": "priya@example.com",
            "mobile": "",
            "password": "SecurePass123",
        },
    )
    assert registration.status_code == 201
    assert registration.json()["user"]["roles"] == ["student"]

    profile = await client.get("/api/v1/auth/me")
    assert profile.status_code == 200
    assert profile.json()["email"] == "priya@example.com"

    refresh = await client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200
    assert refresh.json()["user"]["full_name"] == "Priya Shah"


async def test_duplicate_email_is_rejected(client: AsyncClient) -> None:
    payload = {"full_name": "Priya Shah", "email": "same@example.com", "password": "SecurePass123"}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    duplicate = await client.post("/api/v1/auth/register", json=payload)
    assert duplicate.status_code == 409
