import unittest
from pathlib import Path

from FtpDownloadClient import FtpDownloadClient


class TestFtpConnection(unittest.TestCase):
    pass


class TestFolderCreation(unittest.TestCase):

    def test_folder_exists(self):

        # Arrange
        client = FtpDownloadClient(
            download_directory=Path("."),
            ftp_server_address="test",
            ftp_source_path="test",
        )

        # Act
        client._create_folder("test")

        # Assert
        self.assertTrue(Path("test").exists())

        # (Teardown)
        # - usually represented by a separate method, which is reused across all tests in the class
        # - most unit tests don't need a teardown.

        Path("test").rmdir()
