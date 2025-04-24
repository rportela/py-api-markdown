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
        assert folder_path is not None, "folder_path cannot be None"
        self._folder_path = folder_path

    def put_bytes(self, path: str, filename: str, data: bytes) -> None:
        """
        Save bytes to a file.
        :param path: The directory path where the file will be saved.
        :param filename: The name of the file to save.
        :param data: The bytes data to save.
        """
        assert path is not None, "path cannot be None"
        assert filename is not None, "filename cannot be None"
        assert data is not None, "data cannot be None"
        os.makedirs(os.path.join(self._folder_path, path), exist_ok=True)
        with open(os.path.join(self._folder_path, path, filename), "wb") as f:
            f.write(data)

    def get_bytes(self, path: str, filename: str) -> bytes | None:
        """
        Retrieve bytes from a file.
        :param path: The directory path where the file is located.
        :param filename: The name of the file to retrieve.
        :return: The bytes data read from the file.
        """
        assert path is not None, "path cannot be None"
        assert filename is not None, "filename cannot be None"
        file_path = os.path.join(self._folder_path, path, filename)
        if not os.path.exists(file_path):
            return None
        with open(file_path, "rb") as f:
            return f.read()

    def has_bytes(self, path: str, filename: str) -> bool:
        """
        Check if a file exists.
        :param path: The directory path where the file is located.
        :param filename: The name of the file to check.
        :return: True if the file exists, False otherwise.
        """
        assert path is not None, "path cannot be None"
        assert filename is not None, "filename cannot be None"
        file_path = os.path.join(self._folder_path, path, filename)
        return os.path.exists(file_path)

    def get_bytes_date(self, path: str, filename: str) -> datetime | None:
        """
        Retrieve the last modified date of a file.
        :param path: The directory path where the file is located.
        :param filename: The name of the file to check.
        :return: The last modified date of the file.
        """
        assert path is not None, "path cannot be None"
        assert filename is not None, "filename cannot be None"
        file_path = os.path.join(self._folder_path, path, filename)
        if not os.path.exists(file_path):
            return None
        return datetime.fromtimestamp(os.path.getmtime(file_path))
