from datetime import datetime
from app.repositories.BytesRepository import BytesRepository
import os


class LocalFolderRepo(BytesRepository):
    """
    LocalFolderRepo is a class that implements the BytesRepository interface.
    It is used to store and retrieve bytes data from a local folder.
    """

    _folder_path: str

    def __init__(self, folder_path: str):
        """
        Initialize the LocalFolderRepo with the given folder path.

        :param folder_path: The path to the local folder where data will be stored.
        """
        self._folder_path = folder_path

    def put_bytes(self, path: str, filename: str, data: bytes) -> None:
        raise NotImplementedError

    def get_bytes(self, path: str, filename: str) -> bytes | None:
        raise NotImplementedError

    def has_bytes(self, path: str, filename: str) -> bool:
        raise NotImplementedError

    def get_bytes_date(self, path: str, filename: str) -> datetime | None:
        raise NotImplementedError

