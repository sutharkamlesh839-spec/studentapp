from fastapi import APIRouter

from app.api.deps import DB, CurrentUser
from app.schemas.auth import DashboardSummary
from app.services.auth_service import AuthService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(db: DB, current_user: CurrentUser) -> DashboardSummary:
    """Return a real, intentionally sparse summary until activity modules are enabled."""
    return DashboardSummary(user=await AuthService.user_response(db, current_user), next_actions=[], data_status="awaiting_activity")
