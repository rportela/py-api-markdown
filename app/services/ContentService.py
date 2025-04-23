from base64 import b64encode
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from app.repositories.HashedContentSorage import (
    HashedContentSorage,
    HashedContentStatus,
)
from app.services.MarkdownService import MarkdownService


class ContentUploadRequest(BaseModel):
    content_bytes: bytes
    content_type: str
    filename: Optional[str] = None
    modified_at: Optional[str] = None
    metadata: Optional[dict] = None
    overwrite: Optional[bool] = False
    markdown_it: Optional[bool] = False
    collection_name: Optional[str] = None


class ContentDownloadResponse(BaseModel):
    hash: str
    content_b64: str
    content_type: str
    filename: Optional[str] = None
    modified_at: Optional[str] = None
    metadata: Optional[dict] = None


class ContentService:

    _storage: HashedContentSorage
    _md: MarkdownService

    def __init__(self, storage: HashedContentSorage):
        self._storage = storage
        self._md = MarkdownService(storage)

    def get_status(self, hash: str) -> HashedContentStatus | None:
        return self._storage.get_status(hash)

    def get_original(self, hash: str) -> ContentDownloadResponse | None:
        info = self._storage.get_status(hash)
        if info is None:
            return None
        content_bytes = self._storage.get_original(hash)
        if content_bytes is None:
            return None
        content_b64 = b64encode(content_bytes).decode("utf-8")
        return ContentDownloadResponse(
            hash=info.hash,
            content_b64=content_b64,
            content_type=info.content_type,
            filename=info.filename,
            modified_at=info.modified_at,
            metadata=info.metadata,
        )

    def get_markdown(self, hash: str) -> str | None:
        return self._md.get_markdown(hash)

    def upload(self, req: ContentUploadRequest) -> HashedContentStatus:
        status = self._storage.ensure_content(
            content_type=req.content_type,
            content_bytes=req.content_bytes,
            filename=req.filename,
            modified_at=(
                datetime.fromisoformat(req.modified_at) if req.modified_at else None
            ),
            overwrite=req.overwrite or False,
            metadata=req.metadata,
        )
        if req.markdown_it:
            self._md.ensure_markdown(status, req.content_bytes)
        return status
