from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

from app.api.deps import DB, CurrentUser
from app.api.v1.endpoints.resources import ensure_resource_access
from app.models.resources import Resource
from app.services.storage import storage

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/{resource_id}/download")
async def download_resource(resource_id: UUID, db: DB, current_user: CurrentUser):
    resource = await db.get(Resource, resource_id)
    if not resource or not resource.is_active:
        raise HTTPException(status_code=404, detail="Resource not found")
    await ensure_resource_access(db, current_user, resource)
    if resource.file_key:
        if storage.driver == "s3":
            return RedirectResponse(await storage.presign_download(resource.file_key, resource.file_name))
        path = storage.local_path(resource.file_key)
        if path.exists():
            return FileResponse(path, filename=resource.file_name, media_type=resource.mime_type)
    if resource.source:
        return RedirectResponse(resource.source)
    raise HTTPException(status_code=404, detail="This resource has no downloadable file")
