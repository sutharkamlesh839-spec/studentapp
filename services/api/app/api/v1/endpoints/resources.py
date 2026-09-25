from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import or_, select

from app.api.deps import DB, CurrentUser, require_permission
from app.core.config import settings
from app.models.profiles import StudentProfile
from app.models.resources import Resource, ResourceBookmark, ResourceProgress
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.resources import CatalogSyncResponse, ResourceCreate, ResourceProgressRequest, ResourceResponse
from app.services.audit_service import record_audit
from app.services.icai_catalog import ICAI_CATALOG
from app.services.storage import storage

router = APIRouter(prefix="/resources", tags=["resources"])
ContentPublisher = Depends(require_permission("content.publish"))
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".doc", ".docx", ".xls", ".xlsx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


async def ensure_resource_access(db: DB, user: User, resource: Resource) -> None:
    """Students can only access resources for their own CA level."""
    if "student" not in {role.code for role in user.roles}:
        return
    profile = await db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    if not profile or profile.level != resource.level:
        raise HTTPException(status_code=404, detail="Resource not found")


def to_response(resource: Resource, bookmark_ids: set[UUID], completed_ids: set[UUID]) -> ResourceResponse:
    return ResourceResponse(
        id=resource.id,
        title=resource.title,
        description=resource.description,
        level=resource.level,
        group_name=resource.group_name,
        subject=resource.subject,
        chapter=resource.chapter,
        resource_type=resource.resource_type,
        attempt=resource.attempt,
        year=resource.year,
        source=resource.source,
        file_name=resource.file_name,
        file_size=resource.file_size,
        mime_type=resource.mime_type,
        official_icai=resource.official_icai,
        is_active=resource.is_active,
        bookmarked=resource.id in bookmark_ids,
        completed=resource.id in completed_ids,
        created_at=resource.created_at,
    )


async def user_resource_state(db: DB, user: User, resource_ids: list[UUID]) -> tuple[set[UUID], set[UUID]]:
    if not resource_ids:
        return set(), set()
    bookmarks = await db.scalars(
        select(ResourceBookmark.resource_id).where(
            ResourceBookmark.user_id == user.id,
            ResourceBookmark.resource_id.in_(resource_ids),
        )
    )
    progress = await db.scalars(
        select(ResourceProgress.resource_id).where(
            ResourceProgress.user_id == user.id,
            ResourceProgress.resource_id.in_(resource_ids),
            ResourceProgress.completed.is_(True),
        )
    )
    return set(bookmarks.all()), set(progress.all())


@router.get("", response_model=list[ResourceResponse])
async def list_resources(
    db: DB,
    current_user: CurrentUser,
    q: str | None = None,
    level: str | None = None,
    subject: str | None = None,
    resource_type: str | None = None,
    chapter: str | None = None,
) -> list[ResourceResponse]:
    query = select(Resource).where(Resource.is_active.is_(True)).order_by(Resource.created_at.desc()).limit(500)
    roles = {role.code for role in current_user.roles}
    if "student" in roles:
        profile = await db.scalar(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
        if not profile:
            return []
        query = query.where(Resource.level == profile.level)
    elif level:
        query = query.where(Resource.level == level)
    if q:
        search = f"%{q.strip()}%"
        query = query.where(or_(Resource.title.ilike(search), Resource.subject.ilike(search), Resource.chapter.ilike(search)))
    if subject:
        query = query.where(Resource.subject == subject)
    if chapter:
        query = query.where(Resource.chapter == chapter)
    if resource_type:
        query = query.where(Resource.resource_type == resource_type)
    resources = list((await db.scalars(query)).all())
    bookmark_ids, completed_ids = await user_resource_state(db, current_user, [resource.id for resource in resources])
    return [to_response(resource, bookmark_ids, completed_ids) for resource in resources]


@router.post("/sync-icai", response_model=CatalogSyncResponse)
async def sync_icai_catalog(request: Request, db: DB, current_user: User = ContentPublisher) -> CatalogSyncResponse:
    """Index official ICAI links without copying ICAI's copyrighted files."""
    created = 0
    updated = 0
    for item in ICAI_CATALOG:
        resource = await db.scalar(select(Resource).where(Resource.title == item["title"], Resource.official_icai.is_(True)))
        if resource:
            resource.level = item["level"]
            resource.subject = item["subject"]
            resource.chapter = item["chapter"]
            resource.official_icai = True
            resource.is_active = True
            updated += 1
            continue
        resource = Resource(
            title=item["title"],
            description="Official ICAI study material link. The source page contains the latest applicable edition and chapter/unit links.",
            level=item["level"],
            subject=item["subject"],
            chapter=item["chapter"],
            resource_type="Official ICAI Study Material",
            source=item["source"],
            official_icai=True,
            created_by=current_user.id,
        )
        db.add(resource)
        created += 1
    await record_audit(db, actor_id=current_user.id, action="resource.icai_catalog_synced", resource_type="resource_catalog", after_state={"created": created, "updated": updated}, request_id=request.headers.get("x-request-id"))
    await db.commit()
    return CatalogSyncResponse(created=created, updated=updated, total=len(ICAI_CATALOG), source="https://www.icai.org/post/study-material-nset")


@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    payload: ResourceCreate,
    request: Request,
    db: DB,
    current_user: User = ContentPublisher,
) -> ResourceResponse:
    resource = Resource(**payload.model_dump(), created_by=current_user.id)
    db.add(resource)
    await db.flush()
    await record_audit(
        db,
        actor_id=current_user.id,
        action="resource.created",
        resource_type="resource",
        resource_id=str(resource.id),
        after_state={"title": resource.title, "resource_type": resource.resource_type},
        request_id=request.headers.get("x-request-id"),
    )
    await db.commit()
    await db.refresh(resource)
    return to_response(resource, set(), set())


@router.post("/upload", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_resource(
    request: Request,
    db: DB,
    current_user: User = ContentPublisher,
    file: UploadFile | None = File(default=None),  # noqa: B008
    title: str = Form(..., min_length=2, max_length=220),
    description: str | None = Form(default=None),
    level: str = Form(..., min_length=2, max_length=40),
    group_name: str | None = Form(default=None),
    subject: str = Form(..., min_length=2, max_length=120),
    chapter: str | None = Form(default=None),
    resource_type: str = Form(..., min_length=2, max_length=60),
    attempt: str | None = Form(default=None),
    year: int | None = Form(default=None),
    source: str | None = Form(default=None),
    official_icai: bool = Form(default=False),
) -> ResourceResponse:
    if file is not None:
        extension = Path(file.filename or "").suffix.lower()
        if extension not in ALLOWED_EXTENSIONS or (file.content_type and file.content_type not in ALLOWED_MIME_TYPES):
            raise HTTPException(status_code=415, detail="File type is not permitted")
        content = await file.read(settings.upload_max_bytes + 1)
        if len(content) > settings.upload_max_bytes:
            raise HTTPException(status_code=413, detail="File is larger than the configured upload limit")
    else:
        content = None
        extension = ""

    resource = Resource(
        title=title.strip(),
        description=description,
        level=level,
        group_name=group_name,
        subject=subject,
        chapter=chapter,
        resource_type=resource_type,
        attempt=attempt,
        year=year,
        source=source,
        official_icai=official_icai,
        created_by=current_user.id,
        file_name=Path(file.filename or "").name if file else None,
        file_size=len(content) if content is not None else None,
        mime_type=file.content_type if file else None,
    )
    db.add(resource)
    await db.flush()

    if content is not None and file is not None:
        safe_name = Path(file.filename or f"resource{extension}").name.replace(" ", "-")
        relative_key = f"resources/{resource.id}/{uuid4().hex}-{safe_name}"
        await storage.put(relative_key, content, file.content_type)
        resource.file_key = relative_key

    await record_audit(
        db,
        actor_id=current_user.id,
        action="resource.uploaded",
        resource_type="resource",
        resource_id=str(resource.id),
        after_state={"title": resource.title, "file_name": resource.file_name, "file_size": resource.file_size},
        request_id=request.headers.get("x-request-id"),
    )
    await db.commit()
    await db.refresh(resource)
    return to_response(resource, set(), set())


@router.post("/{resource_id}/bookmark", response_model=MessageResponse)
async def toggle_bookmark(resource_id: UUID, db: DB, current_user: CurrentUser) -> MessageResponse:
    resource = await db.get(Resource, resource_id)
    if not resource or not resource.is_active:
        raise HTTPException(status_code=404, detail="Resource not found")
    await ensure_resource_access(db, current_user, resource)
    bookmark = await db.scalar(
        select(ResourceBookmark).where(
            ResourceBookmark.user_id == current_user.id,
            ResourceBookmark.resource_id == resource_id,
        )
    )
    if bookmark:
        await db.delete(bookmark)
        message = "Removed from your library"
    else:
        db.add(ResourceBookmark(user_id=current_user.id, resource_id=resource_id))
        message = "Saved to your library"
    await db.commit()
    return MessageResponse(message=message)


@router.patch("/{resource_id}/progress", response_model=MessageResponse)
async def update_progress(
    resource_id: UUID,
    payload: ResourceProgressRequest,
    db: DB,
    current_user: CurrentUser,
) -> MessageResponse:
    resource = await db.get(Resource, resource_id)
    if not resource or not resource.is_active:
        raise HTTPException(status_code=404, detail="Resource not found")
    await ensure_resource_access(db, current_user, resource)
    progress = await db.scalar(
        select(ResourceProgress).where(
            ResourceProgress.user_id == current_user.id,
            ResourceProgress.resource_id == resource_id,
        )
    )
    if not progress:
        progress = ResourceProgress(user_id=current_user.id, resource_id=resource_id)
        db.add(progress)
    progress.completed = payload.completed
    progress.last_viewed_at = datetime.now(UTC)
    await db.commit()
    return MessageResponse(message="Progress updated")
