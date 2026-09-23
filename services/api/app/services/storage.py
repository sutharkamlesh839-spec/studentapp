from pathlib import Path
from typing import Protocol

from app.core.config import settings


class StorageService(Protocol):
    async def put(self, key: str, content: bytes, content_type: str | None = None) -> None: ...
    async def presign_download(self, key: str, filename: str | None = None) -> str: ...
    def local_path(self, key: str) -> Path: ...


class ConfiguredStorage:
    """Private local storage for development and S3/R2 for production."""

    def __init__(self) -> None:
        self.driver = settings.storage_driver
        self.root = Path(settings.local_storage_path)
        self._client = None
        if self.driver == "s3":
            try:
                import boto3
            except ImportError as exc:  # pragma: no cover - caught during production boot
                raise RuntimeError("Install boto3 when STORAGE_DRIVER=s3") from exc
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint_url,
                region_name=settings.s3_region,
                aws_access_key_id=settings.s3_access_key_id,
                aws_secret_access_key=settings.s3_secret_access_key,
            )

    def local_path(self, key: str) -> Path:
        candidate = (self.root / key).resolve()
        root = self.root.resolve()
        if root not in candidate.parents:
            raise ValueError("Storage key escapes the configured storage root")
        return candidate

    async def put(self, key: str, content: bytes, content_type: str | None = None) -> None:
        if self.driver == "s3":
            import asyncio

            def upload() -> None:
                assert self._client is not None
                extra = {"ContentType": content_type} if content_type else {}
                self._client.put_object(Bucket=settings.s3_bucket, Key=key, Body=content, **extra)

            await asyncio.to_thread(upload)
            return
        path = self.local_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    async def presign_download(self, key: str, filename: str | None = None) -> str:
        if self.driver != "s3":
            return str(self.local_path(key))
        import asyncio

        def sign() -> str:
            assert self._client is not None
            params = {"Bucket": settings.s3_bucket, "Key": key}
            if filename:
                params["ResponseContentDisposition"] = f'attachment; filename="{filename}"'
            return self._client.generate_presigned_url("get_object", Params=params, ExpiresIn=300)

        return await asyncio.to_thread(sign)


storage = ConfiguredStorage()
