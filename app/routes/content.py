
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UploadRequest(BaseModel):
    content_type: str
    content_bytes: bytes
    filename: Optional[str] = None
    modified_at: Optional[datetime] = None
    index_name: Optional[str] = None
    markdown_it: Optional[bool] = None
    metadata: Optional[dict] = None