import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./data/test-studentos.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-that-is-long-enough-for-local-tests")
os.environ.setdefault("APP_ENV", "test")

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all Phase 0 and learning tables with metadata
from app.db.base import Base
from app.db.session import get_db
from app.main import app


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

    app.dependency_overrides[get_db] = override_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
