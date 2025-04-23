from datetime import datetime, timezone
from io import BytesIO
from typing import Optional
from app.repositories.HashedContentSorage import (
    HashedContentSorage,
    HashedContentStatus,
)
from markitdown import MarkItDown, StreamInfo

MD_FILENAME = "original.md"


class MarkdownService:
    """
    Service to handle markdown content.
    """

    _content_storage: HashedContentSorage
    _markitdown: MarkItDown

    def __init__(self, content_storage: HashedContentSorage):
        """
        Initialize the MarkdownContentService with a HashedContentSorage.
        """
        self._content_storage = content_storage
        self._markitdown = MarkItDown(enable_builtins=True, enable_plugins=True)

    def get_markdown(self, hash: str) -> str | None:
        """
        Returns the markdown content.
        """
        md = self._content_storage.get_bytes(hash, MD_FILENAME)
        return md.decode("utf-8") if md else None

    def ensure_markdown(
        self,
        info: HashedContentStatus,
        content_bytes: bytes,
    ) -> str:
        """
        Ensure the markdown content is stored.
        """
        md = self.get_markdown(info.hash)
        if md is not None:
            return md
        md = self._markitdown.convert_stream(
            BytesIO(content_bytes),
            stream_info=StreamInfo(
                mimetype=info.content_type,
                extension=info.filename.split(".")[-1] if info.filename else None,
                filename=info.filename,
            ),
        ).markdown
        info.markdown_date = datetime.now(tz=timezone.utc).isoformat()
        self._content_storage.set_status(info)
        self._content_storage.put_bytes(info.hash, MD_FILENAME, md.encode("utf-8"))
        return md
