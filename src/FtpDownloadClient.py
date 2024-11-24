import ftplib
import logging
from pathlib import Path


class FtpDownloadClient:
    def __init__(
        self,
        download_directory: Path,
        ftp_server_address: str = "oda.ft.dk",
        ftp_source_path: str = "ODAXML/Referat/samling",
    ):
        self.download_directory = download_directory
        self.ftp_server_address = ftp_server_address
        self.ftp_source_path = ftp_source_path

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def _connect_to_ftp_server(self):
        """
        This method connects to the oda.ft.dk database via ftp and returns a connection object
        """

        try:
            ftp_connection = ftplib.FTP(self.ftp_server_address)
            ftp_connection.login()

        except ftplib.all_errors as e:
            logging.error("Failed to connect or log in to the FTP server: %s", e)
            raise

        return ftp_connection

    def _navigate_to_ftp_source_path(self, ftp_connection):

        try:
            # navigate to the directory where meeting notes are stored
            ftp_connection.cwd(self.ftp_source_path)
        except ftplib.error_perm as e:
            logging.error("Failed to go to specified directory: %s", e)
            raise

        return ftp_connection

    def _create_folder(self, folder):
        """
        This method creates the output directory where the files are downloaded to
        """

        # Check if the root path exists and create it if not
        root = Path(self.download_directory)
        if not root.exists():
            root.mkdir()

        # Check if the folder exists and create it if not
        subfolder = root / folder
        if not subfolder.exists():
            logging.info("Creating %s", subfolder)
            subfolder.mkdir()

    def download_files(self, ftp_connection):
        """
        This method creates downloads the files
        """

        # Download counter is used for logging how many new files were downloaded
        downloaded_counter = 0

        # Get folders
        folders = ftp_connection.nlst()

        for folder in folders:
            self._create_folder(folder)

            ftp_connection.cwd(folder)

            files = ftp_connection.nlst()

            for file in files:
                file_name = f"{self.download_directory}/{folder}/{file}"

                if Path(file_name).exists():
                    logging.debug("%s already downloaded.", file)

                else:
                    with open(file_name, "wb") as f:
                        ftp_connection.retrbinary(f"RETR {file}", f.write)

                    logging.info(
                        "Downloaded %s to %s",
                        file,
                        f"{self.download_directory}/{folder}",
                    )
                    downloaded_counter += 1

            ftp_connection.cwd("..")

        logging.info("%s new files were downloaded.", downloaded_counter)
        ftp_connection.quit()

    def run(self):
        connection = self._connect_to_ftp_server()
        connection = self._navigate_to_ftp_source_path(connection)
        self.download_files(connection)
