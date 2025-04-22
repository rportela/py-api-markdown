from datetime import datetime
from typing import Optional
from app.repositories.HashedContentSorage import (
    HashedContentSorage,
    HashedContentStatus,
)


class MarkdownContentService:
    """
    Service to handle markdown content.
    """

    _content_storage: HashedContentSorage

    def __init__(self, content_storage: HashedContentSorage):
        """
        Initialize the MarkdownContentService with a HashedContentSorage.
        """
        self._content_storage = content_storage

    def ensure_markdown(
        self,
        content_type: str,
        content_bytes: bytes,
        filename: Optional[str] = None,
        modified_at: Optional[datetime] = None,
        overwrite: bool = False,
    ) -> HashedContentStatus:
        """
        Ensure the markdown content is stored.
        """
        info = self._content_storage.ensure_content(
            content_type=content_type,
            content_bytes=content_bytes,
            filename=filename,
            modified_at=modified_at,
            overwrite=overwrite,
        )
        if info.markdown_date is None:
            markdownit 
        return hashed

    def get_content(self) -> str:
        """
        Returns the markdown content.
        """
        return self.content
