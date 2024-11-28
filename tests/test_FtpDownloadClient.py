import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from FtpDownloadClient import FtpDownloadClient


class TestFtpConnection(unittest.TestCase):

    def setUp(self):
        self.client = FtpDownloadClient(
            download_directory=Path("."),
            ftp_server_address="ftp.test.server",
            ftp_source_path="/test/path",
        )

    @patch("ftplib.FTP")
    def test_successful_connection(self, mock_ftp_class):

        mock_ftp_class.return_value = Mock()

        self.client._connect_to_ftp_server()

        mock_ftp_class.assert_called_with("ftp.test.server")

    @patch("ftplib.FTP")
    def test_failed_connection(self, mock_ftp_class):

        mock_ftp_class.side_effect = Exception("Connection failed.")

        with self.assertRaises(Exception):
            self.client._connect_to_ftp_server()


class TestFtpNaviagtionToSourcepath(unittest.TestCase):

    def setUp(self):
        self.client = FtpDownloadClient(
            download_directory=Path("."),
            ftp_server_address="ftp.test.server",
            ftp_source_path="/test/path",
        )

    @patch("ftplib.FTP")
    def test_successful_navigation_to_source_path(self, mock_ftp_class):

        mock_ftp_instance = Mock()
        mock_ftp_class.return_value = mock_ftp_instance

        self.client._navigate_to_ftp_source_path(mock_ftp_instance)

        mock_ftp_instance.cwd.assert_called_with("/test/path")
