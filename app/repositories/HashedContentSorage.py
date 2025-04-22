from datetime import datetime, timezone
from typing import Optional

from blake3 import blake3
from pydantic import BaseModel

from app.repositories.BytesRepository import BytesRepository


class HashedContentStatus(BaseModel):
    hash: str
    size: int
    content_type: str
    modified_at: str
    filename: Optional[str] = None
    markdown_date: Optional[str] = None
    markdown_error: Optional[str] = None


class HashedContentSorage:
    """
    Abstract class for storing and retrieving hashed content.
    """

    _byte_repo: BytesRepository

    def __init__(self, byte_repo: BytesRepository):
        """
        Initialize the HashedContentStorage with a BytesRepository.
        """
        self._byte_repo = byte_repo

    def get_original(self, hash: str) -> bytes | None:
        """
        Get the original content by its hash.
        """
        return self._byte_repo.get_bytes(hash, "original.bin")

    def get_status(self, hash: str) -> HashedContentStatus | None:
        """
        Get the status of the content by its hash.
        """
        status_bytes = self._byte_repo.get_bytes(hash, "index.json")
        if status_bytes is None:
            return None
        return HashedContentStatus.model_validate_json(status_bytes)

    def put_bytes(self, hash: str, filename: str, data: bytes) -> None:
        """
        Save bytes to a file.

        :param path: The directory path where the file will be saved.
        :param filename: The name of the file to save.
        :param data: The bytes data to save.
        """
        return self._byte_repo.put_bytes(hash, filename, data)

    def get_bytes(self, hash: str, filename: str) -> bytes | None:
        """
        Retrieve bytes from a file.

        :param path: The directory path where the file is located.
        :param filename: The name of the file to retrieve.
        :return: The bytes data read from the file.
        """
        return self._byte_repo.get_bytes(hash, filename)

    def has_bytes(self, hash: str, filename: str) -> bool:
        """
        Check if a file exists.

        :param path: The directory path where the file is located.
        :param filename: The name of the file to check.
        :return: True if the file exists, False otherwise.
        """
        return self._byte_repo.has_bytes(hash, filename)

    def get_bytes_date(self, path: str, filename: str) -> datetime | None:
        """
        Retrieve the last modified date of a file.

        :param path: The directory path where the file is located.
        :param filename: The name of the file to check.
        :return: The last modified date of the file.
        """
        return self._byte_repo.get_bytes_date(path, filename)

    def ensure_content(
        self,
        content_type: str,
        content_bytes: bytes,
        filename: Optional[str] = None,
        modified_at: Optional[datetime] = None,
        overwrite: bool = False,
    ) -> HashedContentStatus:
        """
        Ensure the content is stored and return its hash.
        """
        assert content_bytes is not None, "Content bytes cannot be None"
        assert content_type is not None, "Content type cannot be None"
        hash = blake3(content_bytes).hexdigest()
        status_file = "index.json"
        status_bytes = self._byte_repo.get_bytes(hash, status_file)
        if status_bytes is None or overwrite:
            self._byte_repo.put_bytes(hash, "original.bin", content_bytes)
            status = HashedContentStatus(
                hash=hash,
                size=len(content_bytes),
                content_type=content_type,
                modified_at=(
                    modified_at.isoformat()
                    if modified_at
                    else datetime.now(tz=timezone.utc).isoformat()
                ),
                filename=filename,
            )
            status_bytes = status.model_dump_json().encode("utf-8")
            self._byte_repo.put_bytes(hash, status_file, status_bytes)
        else:
            status_bytes = self._byte_repo.get_bytes(hash, status_file)
            assert status_bytes is not None, "Status bytes cannot be None"
            status = HashedContentStatus.model_validate_json(status_bytes)
        return status
