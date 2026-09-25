from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import DB, CurrentUser
from app.models.learning import MCQResponse, RevisionItem, SyllabusItem
from app.models.resources import ResourceProgress
from app.schemas.auth import DashboardSummary
from app.services.auth_service import AuthService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(db: DB, current_user: CurrentUser) -> DashboardSummary:
    """Return persisted activity metrics for the signed-in student's dashboard."""
    attempts = await db.scalar(select(func.count(MCQResponse.id)).where(MCQResponse.user_id == current_user.id)) or 0
    correct = await db.scalar(select(func.count(MCQResponse.id)).where(MCQResponse.user_id == current_user.id, MCQResponse.is_correct.is_(True))) or 0
    mcq_accuracy = (correct / attempts) * 100 if attempts else 0

    syllabus_items = list((await db.scalars(select(SyllabusItem).where(SyllabusItem.user_id == current_user.id))).all())
    syllabus_completion = (
        sum((item.completed_topics / item.total_topics) * 100 for item in syllabus_items) / len(syllabus_items)
        if syllabus_items
        else 0
    )
    completed_resources = await db.scalar(
        select(func.count(ResourceProgress.id)).where(
            ResourceProgress.user_id == current_user.id,
            ResourceProgress.completed.is_(True),
        )
    ) or 0
    pending_revision = await db.scalar(
        select(func.count(RevisionItem.id)).where(
            RevisionItem.user_id == current_user.id,
            RevisionItem.status != "completed",
        )
    ) or 0

    next_actions: list[str] = []
    if not attempts:
        next_actions.append("Start your first MCQ practice session")
    elif mcq_accuracy < 70:
        next_actions.append("Review your wrong answers before the next test")
    if not syllabus_items:
        next_actions.append("Open the syllabus tracker to set your chapter plan")
    elif syllabus_completion < 50:
        next_actions.append("Complete one syllabus chapter this week")
    if not completed_resources:
        next_actions.append("Read and complete your first study resource")
    if pending_revision:
        next_actions.append(f"You have {pending_revision} revision item{'s' if pending_revision != 1 else ''} due")

    score_parts = [mcq_accuracy, syllabus_completion]
    preparation_score = round(sum(score_parts) / len(score_parts)) if any(score_parts) else None
    active = bool(attempts or syllabus_items or completed_resources or pending_revision)
    return DashboardSummary(
        user=await AuthService.user_response(db, current_user),
        preparation_score=preparation_score,
        syllabus_completion=round(syllabus_completion, 2) if syllabus_items else None,
        next_actions=next_actions[:4],
        data_status="active" if active else "awaiting_activity",
    )
