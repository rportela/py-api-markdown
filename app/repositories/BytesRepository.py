from abc import ABC, abstractmethod
from datetime import datetime

class BytesRepository(ABC):

    @abstractmethod
    def put_bytes(self, path: str, filename: str, data: bytes) -> None:
        """
        Save bytes to a file.

        :param path: The directory path where the file will be saved.
        :param filename: The name of the file to save.
        :param data: The bytes data to save.
        """

    @abstractmethod
    def get_bytes(self, path: str, filename: str) -> bytes | None:
        """
        Retrieve bytes from a file.

        :param path: The directory path where the file is located.
        :param filename: The name of the file to retrieve.
        :return: The bytes data read from the file.
        """

    @abstractmethod
    def has_bytes(self, path: str, filename: str) -> bool:
        """
        Check if a file exists.

        :param path: The directory path where the file is located.
        :param filename: The name of the file to check.
        :return: True if the file exists, False otherwise.
        """

    @abstractmethod
    def get_bytes_date(self, path: str, filename: str) -> datetime | None:
        """
        Retrieve the last modified date of a file.

        :param path: The directory path where the file is located.
        :param filename: The name of the file to check.
        :return: The last modified date of the file.
        """
