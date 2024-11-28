import ftplib
import logging
from pathlib import Path


class FtpDownloadClient:
    def __init__(
        self,
        download_directory: Path,
        ftp_server_address: str,
        ftp_source_path: str,
        logger: logging.Logger | None = None,
    ):
        self.download_directory: Path = download_directory
        self.ftp_server_address: str = ftp_server_address
        self.ftp_source_path: str = ftp_source_path
        self.logger: logging.Logger | None = logger
        self.ftp_connection: ftplib.FTP | None = None

    def _connect_to_ftp_server(self) -> None:
        """
        This method connects to the ftp server specified in the ftp_server_address
        attribute and assigns an FTP object `self.ftp_connection`.

        Raises:
            `ftplib.all_errors`
        """

        try:
            ftp_connection = ftplib.FTP(self.ftp_server_address)
            _ = ftp_connection.login()

            if self.logger is not None:
                self.logger.info(
                    "Successfully established connection to FTP server: %s",
                    self.ftp_server_address,
                )

        except ftplib.all_errors as e:
            logging.error("Failed to connect or log in to the FTP server: %s", e)
            raise

        self.ftp_connection = ftp_connection

    def _navigate_to_ftp_source_path(self) -> None:
        """
        This method navigates to the file source path specified in the
        `ftp_source_path` attribute.

        Raises:
            `ftplib.error_perm`
        """

        if self.ftp_connection is None:
            raise ValueError(
                "FTP connection is not established.\
                Please initialize the connection before proceeding"
            )

        try:
            _ = self.ftp_connection.cwd(self.ftp_source_path)

            if self.logger is not None:
                self.logger.info(
                    "Successfully navigated to FTP source path: %s",
                    self.ftp_source_path,
                )

        except ftplib.error_perm as e:
            logging.error("Failed to navigate to specified directory: %s", e)
            raise

        self.ftp_connection = self.ftp_connection

    def _create_folder(self, folder: str) -> None:
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
            if self.logger is not None:
                self.logger.info("Creating %s", subfolder)
                subfolder.mkdir()

    def _download_files(self) -> None:
        """
        This method creates a download folder and downloads the files from the ftp
        server
        """

        if self.ftp_connection is None:
            raise ValueError(
                "FTP connection is not established.\
                Please initialize the connection before proceeding"
            )

        # Download counter is used for logging how many new files were downloaded
        downloaded_counter = 0

        # Get folders
        folders = self.ftp_connection.nlst()

        for folder in folders:
            self._create_folder(folder)

            _ = self.ftp_connection.cwd(folder)

            files = self.ftp_connection.nlst()

            for file in files:
                file_name = f"{self.download_directory}/{folder}/{file}"

                if Path(file_name).exists():
                    if self.logger is not None:
                        self.logger.info("%s already downloaded.", file)

                else:
                    with open(file_name, "wb") as f:
                        _ = self.ftp_connection.retrbinary(f"RETR {file}", f.write)

                    if self.logger is not None:
                        self.logger.info(
                            "Downloaded %s to %s",
                            file,
                            f"{self.download_directory}/{folder}",
                        )
                        downloaded_counter += 1

            _ = self.ftp_connection.cwd("..")

        if self.logger is not None:
            self.logger.info("%s new files were downloaded.", downloaded_counter)
            _ = self.ftp_connection.quit()

    def run(self) -> None:
        """
        This method will run the FtpDownloadClient
        """

        self._connect_to_ftp_server()
        self._navigate_to_ftp_source_path()
        self._download_files()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.INFO)

    # Set up a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set level to DEBUG to capture all types of logs

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Set level to DEBUG to captureall logs

    # Create a file handler
    file_handler = logging.FileHandler("example.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s -%(message)s")

    # Add formatter to handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    download_directory = Path(f"{Path(__file__).parent.parent}/data/test")
    server_address = "oda.ft.dk"
    source_path = "ODAXML/Referat/samling"

    client = FtpDownloadClient(
        download_directory=download_directory,
        ftp_server_address=server_address,
        ftp_source_path=source_path,
        logger=logger,
    )

    client.run()
