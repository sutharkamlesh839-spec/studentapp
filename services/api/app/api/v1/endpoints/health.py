from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DB

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api", "timestamp": datetime.now(UTC).isoformat()}


@router.get("/health/ready")
async def readiness(db: DB) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ready", "service": "api", "timestamp": datetime.now(UTC).isoformat()}
