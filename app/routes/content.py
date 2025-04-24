from __future__ import annotations

from fastapi import APIRouter

from app.repositories.HashedContentStorage import (
    HashedContentStorage,
    HashedContentStatus,
)
from app.repositories.LocalFolderRepo import LocalFolderRepo
from app.services.ContentService import (
    ContentService,
    ContentUploadRequest,
    ContentDownloadResponse,
)

router = APIRouter()
storage = LocalFolderRepo("./hashed_files")
hash_storage = HashedContentStorage(storage)
service = ContentService(hash_storage)


@router.post("/v1/content")
async def upload(body: ContentUploadRequest) -> HashedContentStatus:
    return service.upload(body)


@router.get("/v1/content/{hash}")
async def download(hash: str) -> ContentDownloadResponse | None:
    result = service.download(hash)
