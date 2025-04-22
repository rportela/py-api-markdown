

from app.repositories.HashedContentSorage import HashedContentSorage


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

    def ensure_content(self, content: str) -> None:
        """
        Ensure the markdown content is stored.
        """
        assert content is not None, "Content cannot be None"
        self.content = content
        hash = self._content_storage.ensure_content(
            content_type="text/markdown",
            content_bytes=content.encode("utf-8"),
            filename="content.md",
        )
        return hash

    def get_content(self) -> str:
        """
        Returns the markdown content.
        """
        return self.content