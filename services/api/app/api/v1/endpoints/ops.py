from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import or_, select

from app.api.deps import DB, CurrentUser, require_permission
from app.core.config import settings
from app.models.audit import AuditLog
from app.models.learning import Notification
from app.models.ops import OfficialUpdate, Opportunity, PaperSubmission, VideoLesson
from app.models.profiles import StudentProfile
from app.models.rbac import Role
from app.models.user import User
from app.schemas.ops import (
    AdminUserResponse,
    AuditLogResponse,
    OfficialUpdateCreate,
    OfficialUpdateResponse,
    OpportunityCreate,
    OpportunityResponse,
    PaperAssign,
    PaperEvaluate,
    PaperResponse,
    VideoCreate,
    VideoResponse,
)
from app.services.audit_service import record_audit
from app.services.pdf_validation import has_pdf_structure
from app.services.storage import storage

router = APIRouter(tags=["operations"])
ContentPublisher = Depends(require_permission("content.publish"))
UserManager = Depends(require_permission("user.manage"))
PaperEvaluator = Depends(require_permission("evaluation.mark"))
AuditReader = Depends(require_permission("audit.read"))
PAPER_EXTENSIONS = {".pdf"}


def video_response(item: VideoLesson) -> VideoResponse:
    return VideoResponse(
        id=item.id,
        title=item.title,
        description=item.description,
        level=item.level,
        subject=item.subject,
        chapter=item.chapter,
        video_url=item.video_url,
        duration_minutes=item.duration_minutes,
        created_at=item.created_at,
    )


def opportunity_response(item: Opportunity) -> OpportunityResponse:
    return OpportunityResponse(
        id=item.id,
        kind=item.kind,
        title=item.title,
        organisation=item.organisation,
        location=item.location,
        description=item.description,
        application_url=item.application_url,
        target_level=item.target_level,
        created_at=item.created_at,
    )


def update_response(item: OfficialUpdate) -> OfficialUpdateResponse:
    return OfficialUpdateResponse(
        id=item.id,
        title=item.title,
        body=item.body,
        category=item.category,
        source_url=item.source_url,
        published_at=item.published_at,
    )


async def ensure_paper_access(db: DB, user: User, paper: PaperSubmission) -> None:
    roles = {role.code for role in user.roles}
    if "student" in roles and not roles.intersection({"admin", "super_admin"}) and paper.student_id != user.id:
        raise HTTPException(status_code=404, detail="Paper not found")
    if "faculty" in roles and not roles.intersection({"admin", "super_admin"}) and paper.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="This paper is not assigned to you")
    if not roles.intersection({"student", "faculty", "admin", "super_admin"}):
        raise HTTPException(status_code=403, detail="You do not have access to this paper")


def paper_response(item: PaperSubmission) -> PaperResponse:
    return PaperResponse(
        id=item.id,
        title=item.title,
        subject=item.subject,
        file_name=item.file_name,
        annotated_file_name=item.annotated_file_name,
        status=item.status,
        marks=item.marks,
        feedback=item.feedback,
        assigned_to=item.assigned_to,
        created_at=item.created_at,
        evaluated_at=item.evaluated_at,
    )


async def student_level(db: DB, user: User) -> str | None:
    profile = await db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    return profile.level if profile else None


@router.get("/videos", response_model=list[VideoResponse])
async def list_videos(db: DB, current_user: CurrentUser, subject: str | None = None) -> list[VideoResponse]:
    query = select(VideoLesson).where(VideoLesson.is_active.is_(True)).order_by(VideoLesson.created_at.desc()).limit(100)
    if "student" in {role.code for role in current_user.roles}:
        level = await student_level(db, current_user)
        if not level:
            return []
        query = query.where(VideoLesson.level == level)
    if subject:
        query = query.where(VideoLesson.subject == subject)
    return [video_response(item) for item in (await db.scalars(query)).all()]


@router.post("/videos", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video(payload: VideoCreate, db: DB, current_user: User = ContentPublisher) -> VideoResponse:
    data = payload.model_dump()
    data["video_url"] = str(payload.video_url)
    item = VideoLesson(**data, created_by=current_user.id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return video_response(item)


@router.get("/opportunities", response_model=list[OpportunityResponse])
async def list_opportunities(db: DB, current_user: CurrentUser, kind: str | None = None) -> list[OpportunityResponse]:
    query = select(Opportunity).where(Opportunity.is_active.is_(True)).order_by(Opportunity.created_at.desc()).limit(100)
    if kind:
        query = query.where(Opportunity.kind == kind)
    if "student" in {role.code for role in current_user.roles}:
        level = await student_level(db, current_user)
        query = query.where(or_(Opportunity.target_level.is_(None), Opportunity.target_level == level))
    return [opportunity_response(item) for item in (await db.scalars(query)).all()]


@router.post("/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(payload: OpportunityCreate, db: DB, current_user: User = ContentPublisher) -> OpportunityResponse:
    data = payload.model_dump()
    data["application_url"] = str(payload.application_url) if payload.application_url else None
    item = Opportunity(**data, created_by=current_user.id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return opportunity_response(item)


@router.get("/official-updates", response_model=list[OfficialUpdateResponse])
async def list_official_updates(db: DB, _current_user: CurrentUser) -> list[OfficialUpdateResponse]:
    items = (await db.scalars(select(OfficialUpdate).where(OfficialUpdate.is_active.is_(True)).order_by(OfficialUpdate.published_at.desc()).limit(100))).all()
    return [update_response(item) for item in items]


@router.post("/official-updates", response_model=OfficialUpdateResponse, status_code=status.HTTP_201_CREATED)
async def create_official_update(payload: OfficialUpdateCreate, db: DB, current_user: User = ContentPublisher) -> OfficialUpdateResponse:
    item = OfficialUpdate(
        title=payload.title,
        body=payload.body,
        category=payload.category,
        source_url=str(payload.source_url),
        created_by=current_user.id,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return update_response(item)


@router.post("/papers/upload", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    db: DB,
    current_user: CurrentUser,
    file: UploadFile = File(...),  # noqa: B008
    title: str = Form(..., min_length=2, max_length=220),
    subject: str = Form(..., min_length=2, max_length=120),
) -> PaperResponse:
    if "student" not in {role.code for role in current_user.roles}:
        raise HTTPException(status_code=403, detail="Only students can submit papers")
    extension = Path(file.filename or "").suffix.lower()
    if extension not in PAPER_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Paper file type is not permitted")
    content = await file.read(settings.upload_max_bytes + 1)
    if len(content) > settings.upload_max_bytes:
        raise HTTPException(status_code=413, detail="File is larger than the configured upload limit")
    if not has_pdf_structure(content):
        raise HTTPException(status_code=415, detail="Paper must be a readable PDF document")
    item = PaperSubmission(
        student_id=current_user.id,
        title=title.strip(),
        subject=subject.strip(),
        file_name=Path(file.filename or "paper").name,
    )
    db.add(item)
    await db.flush()
    item.file_key = f"papers/{item.id}/{uuid4().hex}-{Path(file.filename or 'paper').name.replace(' ', '-')}"
    await storage.put(item.file_key, content, file.content_type)
    db.add(item)
    await record_audit(db, actor_id=current_user.id, action="paper.submitted", resource_type="paper", resource_id=str(item.id))
    await db.commit()
    await db.refresh(item)
    return paper_response(item)


@router.get("/papers/{paper_id}/download")
async def download_paper(paper_id: UUID, db: DB, current_user: CurrentUser):
    paper = await db.get(PaperSubmission, paper_id)
    if not paper or not paper.file_key:
        raise HTTPException(status_code=404, detail="Paper file not found")
    await ensure_paper_access(db, current_user, paper)
    if storage.driver == "s3":
        return RedirectResponse(await storage.presign_download(paper.file_key, paper.file_name))
    path = storage.local_path(paper.file_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Paper file not found")
    return FileResponse(path, filename=paper.file_name, media_type="application/pdf")


@router.get("/papers/{paper_id}/annotated-download")
async def download_annotated_paper(paper_id: UUID, db: DB, current_user: CurrentUser):
    paper = await db.get(PaperSubmission, paper_id)
    if not paper or not paper.annotated_file_key:
        raise HTTPException(status_code=404, detail="Annotated paper not found")
    await ensure_paper_access(db, current_user, paper)
    if storage.driver == "s3":
        return RedirectResponse(await storage.presign_download(paper.annotated_file_key, paper.annotated_file_name))
    path = storage.local_path(paper.annotated_file_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Annotated paper not found")
    return FileResponse(path, filename=paper.annotated_file_name, media_type="application/pdf")


@router.post("/papers/{paper_id}/annotated", response_model=PaperResponse)
async def upload_annotated_paper(
    paper_id: UUID,
    db: DB,
    current_user: User = PaperEvaluator,
    file: UploadFile = File(...),  # noqa: B008
    marks: float | None = Form(default=None, ge=0, le=1000),
    feedback: str | None = Form(default=None, min_length=2, max_length=10000),
) -> PaperResponse:
    paper = await db.get(PaperSubmission, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    roles = {role.code for role in current_user.roles}
    if "faculty" in roles and not roles.intersection({"admin", "super_admin"}) and paper.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="This paper is outside your assigned scope")
    if Path(file.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(status_code=415, detail="Annotated review must be a PDF")
    content = await file.read(settings.upload_max_bytes + 1)
    if len(content) > settings.upload_max_bytes:
        raise HTTPException(status_code=413, detail="File is larger than the configured upload limit")
    if not has_pdf_structure(content):
        raise HTTPException(status_code=415, detail="Annotated review must be a readable PDF document")
    if (marks is None) != (feedback is None):
        raise HTTPException(status_code=422, detail="Marks and feedback must be provided together")
    paper.annotated_file_key = f"papers/{paper.id}/review-{uuid4().hex}.pdf"
    paper.annotated_file_name = f"reviewed-{Path(paper.file_name or 'paper').stem}.pdf"
    paper.status = "reviewed"
    if marks is not None and feedback is not None:
        paper.marks = marks
        paper.feedback = feedback.strip()
        paper.status = "evaluated"
        paper.evaluated_at = datetime.now(UTC)
    await storage.put(paper.annotated_file_key, content, "application/pdf")
    await record_audit(
        db,
        actor_id=current_user.id,
        action="paper.annotated",
        resource_type="paper",
        resource_id=str(paper.id),
        after_state={"marks": marks, "completed": marks is not None},
    )
    if marks is not None:
        await record_audit(
            db,
            actor_id=current_user.id,
            action="paper.evaluated",
            resource_type="paper",
            resource_id=str(paper.id),
            after_state={"marks": marks},
        )
        db.add(Notification(user_id=paper.student_id, title="Your paper was evaluated", body=paper.title, kind="evaluation"))
    await db.commit()
    await db.refresh(paper)
    return paper_response(paper)


@router.get("/papers", response_model=list[PaperResponse])
async def list_papers(db: DB, current_user: CurrentUser) -> list[PaperResponse]:
    roles = {role.code for role in current_user.roles}
    query = select(PaperSubmission).order_by(PaperSubmission.created_at.desc()).limit(100)
    if "student" in roles and not roles.intersection({"admin", "super_admin", "faculty"}):
        query = query.where(PaperSubmission.student_id == current_user.id)
    elif "faculty" in roles and not roles.intersection({"admin", "super_admin"}):
        query = query.where(PaperSubmission.assigned_to == current_user.id)
    return [paper_response(item) for item in (await db.scalars(query)).all()]


@router.patch("/papers/{paper_id}/assign", response_model=PaperResponse)
async def assign_paper(paper_id: UUID, payload: PaperAssign, db: DB, current_user: User = UserManager) -> PaperResponse:
    paper = await db.get(PaperSubmission, paper_id)
    faculty = await db.scalar(select(User).join(User.roles).where(User.id == payload.faculty_id, Role.code == "faculty"))
    if not paper or not faculty:
        raise HTTPException(status_code=404, detail="Paper or faculty member not found")
    paper.assigned_to = faculty.id
    paper.status = "assigned"
    await record_audit(db, actor_id=current_user.id, action="paper.assigned", resource_type="paper", resource_id=str(paper.id), after_state={"assigned_to": str(faculty.id)})
    await db.commit()
    await db.refresh(paper)
    return paper_response(paper)


@router.post("/papers/{paper_id}/evaluate", response_model=PaperResponse)
async def evaluate_paper(paper_id: UUID, payload: PaperEvaluate, db: DB, current_user: User = PaperEvaluator) -> PaperResponse:
    paper = await db.get(PaperSubmission, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    roles = {role.code for role in current_user.roles}
    if "faculty" in roles and not roles.intersection({"admin", "super_admin"}) and paper.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="This paper is outside your assigned scope")
    paper.marks = payload.marks
    paper.feedback = payload.feedback
    paper.status = "evaluated"
    paper.evaluated_at = datetime.now(UTC)
    await record_audit(db, actor_id=current_user.id, action="paper.evaluated", resource_type="paper", resource_id=str(paper.id), after_state={"marks": payload.marks})
    db.add(Notification(user_id=paper.student_id, title="Your paper was evaluated", body=paper.title, kind="evaluation"))
    await db.commit()
    await db.refresh(paper)
    return paper_response(paper)


@router.get("/admin/users", response_model=list[AdminUserResponse])
async def list_users(db: DB, _current_user: User = UserManager, role: str | None = None) -> list[AdminUserResponse]:
    query = select(User).order_by(User.created_at.desc()).limit(200)
    if role:
        query = query.join(User.roles).where(Role.code == role)
    result = await db.execute(query)
    users = list(result.unique().scalars().all())
    responses = []
    for user in users:
        responses.append(AdminUserResponse(id=user.id, email=user.email, full_name=user.full_name, status=user.status, roles=[item.code for item in user.roles], created_at=user.created_at))
    return responses


@router.get("/admin/audit-logs", response_model=list[AuditLogResponse])
async def list_audit_logs(db: DB, _current_user: User = AuditReader) -> list[AuditLogResponse]:
    items = (await db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200))).all()
    return [AuditLogResponse(id=item.id, actor_id=item.actor_id, action=item.action, resource_type=item.resource_type, resource_id=item.resource_id, after_state=item.after_state, created_at=item.created_at) for item in items]
